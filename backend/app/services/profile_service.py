import uuid
from typing import Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.privacy import PersonPrivacySettings
from app.db.models.audit_log import AuditLog
from app.db.models.notification import NotificationRecipient
from app.db.models.relationship import Relationship

from app.schemas.person import PersonCreate
from app.schemas.profile import (
    PersonProfileUpdate, PrivacySettingsUpdate, PrivacySettingsResponse, 
    ProfileCompletenessResponse, DashboardResponse, FamilySummary,
    NotificationSummary, RelationshipSummary, FamilyOverviewResponse
)
from app.schemas.event import EventResponse
from app.schemas.activity import ActivityResponse
from app.services.privacy_service import PrivacyService
from app.services.event_service import EventService
from app.services.activity_service import ActivityService
from app.services.life_events_service import LifeEventsService
from app.services.person_claim_service import PersonClaimService
from app.services.person_service import PersonService
from app.services.relationship_graph_service import RelationshipGraphService

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.privacy_service = PrivacyService(db)
        self.event_service = EventService(db)
        self.activity_service = ActivityService(db)
        self.graph_service = RelationshipGraphService(db)

    
    def complete_onboarding(self, user_id: uuid.UUID, data: PersonCreate):
        # Verify user has no claimed Person
        existing = self.get_current_user_person(user_id)
        if existing:
            raise HTTPException(status_code=409, detail="User already has a claimed Person.")
            
        # Create canonical Person and claim it atomically-ish (we will use DB transaction)
        # PersonService.create_person commits internally, which breaks atomicity if claim fails.
        # However, we can use the repository directly or just accept the 2-step commit since
        # claim_person rarely fails for a freshly created person by the same user.
        # But for true atomicity, let's do it here:
        from app.db.models.person import Person
        from app.db.models.privacy import PersonPrivacySettings
        from app.db.models.audit_log import AuditLog
        from datetime import datetime, timezone

        try:
            # 1. Create Person
            person = Person(
                **data.model_dump(exclude_unset=True),
                created_by_user_id=user_id,
                claimed_by_user_id=user_id,
                profile_status="claimed"
            )
            self.db.add(person)
            self.db.flush()

            # 2. Setup privacy defaults
            privacy = PersonPrivacySettings(person_id=person.id)
            self.db.add(privacy)

            # 3. Audit log
            audit = AuditLog(
                actor_user_id=user_id,
                action="person.create_and_claim_onboarding",
                entity_type="person",
                entity_id=person.id,
                metadata={"method": "onboarding"}
            )
            self.db.add(audit)
            self.db.commit()
            
            return person
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create and claim person.")

    def get_current_user_person(self, user_id: uuid.UUID) -> Person:
        return self.db.execute(select(Person).where(Person.claimed_by_user_id == user_id)).scalar_one_or_none()

    def update_person_profile(self, user_id: uuid.UUID, data: PersonProfileUpdate) -> Person:
        person = self.get_current_user_person(user_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No claimed person found for user")
            
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(person, key, value)
            
        self.db.add(AuditLog(
            actor_user_id=user_id, action="profile.update", entity_type="person", entity_id=person.id,
            metadata_={"changed_fields": list(update_data.keys())}
        ))
        self.db.commit()
        self.db.refresh(person)
        return person

    def get_privacy_settings(self, user_id: uuid.UUID) -> PersonPrivacySettings:
        person = self.get_current_user_person(user_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No claimed person found")
        return self.privacy_service.get_settings(person.id)
        
    def update_privacy_settings(self, user_id: uuid.UUID, data: PrivacySettingsUpdate) -> PersonPrivacySettings:
        person = self.get_current_user_person(user_id)
        if not person:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No claimed person found")
            
        settings = self.privacy_service.get_settings(person.id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)
            
        self.db.add(AuditLog(
            actor_user_id=user_id, action="privacy.update", entity_type="privacy_settings", entity_id=settings.id,
            metadata_={"changed_fields": list(update_data.keys())}
        ))
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def get_profile_completeness(self, user_id: uuid.UUID) -> ProfileCompletenessResponse:
        person = self.get_current_user_person(user_id)
        if not person:
            return ProfileCompletenessResponse(percentage=0, completed=[], missing=[])
            
        fields = ["first_name", "last_name", "date_of_birth", "gender", "bio", "phone", "email", "birth_place", "current_city"]
        completed = []
        missing = []
        for f in fields:
            if getattr(person, f):
                completed.append(f)
            else:
                missing.append(f)
                
        pct = int(len(completed) / len(fields) * 100) if fields else 0
        return ProfileCompletenessResponse(percentage=pct, completed=completed, missing=missing)

    def get_dashboard(self, user_id: uuid.UUID) -> DashboardResponse:
        person = self.get_current_user_person(user_id)
        profile_summary = self.privacy_service.resolve_safe_person(person, user_id) if person else None
        
        # Family summaries
        families = []
        if person:
            memberships = self.db.execute(select(FamilyMember).where(FamilyMember.person_id == person.id)).scalars().all()
            if memberships:
                family_ids = [m.family_id for m in memberships]
                fam_records = self.db.execute(select(Family).where(Family.id.in_(family_ids))).scalars().all()
                fam_map = {f.id: f for f in fam_records}
                
                count_rows = self.db.execute(
                    select(FamilyMember.family_id, func.count(FamilyMember.person_id))
                    .where(FamilyMember.family_id.in_(family_ids))
                    .group_by(FamilyMember.family_id)
                ).all()
                count_map = {f_id: cnt for f_id, cnt in count_rows}
                
                for mem in memberships:
                    fam = fam_map.get(mem.family_id)
                    if fam:
                        families.append(FamilySummary(
                            id=fam.id, name=fam.name, role=mem.role, member_count=count_map.get(fam.id, 0)
                        ))
                
        # Notifications
        unread = self.db.execute(select(func.count()).where(NotificationRecipient.user_id == user_id, NotificationRecipient.is_read == False)).scalar_one()
        notif_summary = NotificationSummary(unread_count=unread, recent=[])
        
        # Events
        events, _ = self.event_service.list_events(user_id, limit=5, upcoming=True)
        event_responses = [EventResponse.model_validate(e) for e in events]
        
        # Life Events
        life_events = LifeEventsService(self.db).get_upcoming_events(user_id, days=30)
        event_responses.extend(life_events)
        
        # Sort combined events by date
        def get_sort_key(e: EventResponse):
            if e.start_datetime:
                return e.start_datetime.date()
            if e.start_date:
                return e.start_date
            return date.max
        event_responses.sort(key=get_sort_key)
        # Limit total upcoming to 10
        event_responses = event_responses[:10]
        
        # Activity
        activities, _ = self.activity_service.list_activities(user_id, limit=10)
        activity_responses = [ActivityResponse.model_validate(a) for a in activities]
        
        # Relationship Summary
        rel_summary = RelationshipSummary(parents_count=0, children_count=0, siblings_count=0, spouses_count=0)
        if person:
            from sqlalchemy import or_
            # Optimize 4 sequential queries into 1 to reduce Neon DB latency
            rows = self.db.execute(
                select(Relationship.relationship_type, Relationship.person_a_id, Relationship.person_b_id)
                .where(or_(Relationship.person_a_id == person.id, Relationship.person_b_id == person.id))
            ).all()
            
            p_cnt = sum(1 for r in rows if r.relationship_type == 'parent' and r.person_b_id == person.id)
            c_cnt = sum(1 for r in rows if r.relationship_type == 'parent' and r.person_a_id == person.id)
            s_cnt = sum(1 for r in rows if r.relationship_type == 'sibling')
            sp_cnt = sum(1 for r in rows if r.relationship_type == 'spouse')
            
            rel_summary = RelationshipSummary(parents_count=p_cnt, children_count=c_cnt, siblings_count=s_cnt, spouses_count=sp_cnt)
            
        return DashboardResponse(
            profile=profile_summary,
            families=families,
            upcoming_events=event_responses,
            notifications=notif_summary,
            recent_activity=activity_responses,
            relationship_summary=rel_summary
        )

    def get_family_overview(self, family_id: uuid.UUID, user_id: uuid.UUID) -> FamilyOverviewResponse:
        person = self.get_current_user_person(user_id)
        if not person:
            raise HTTPException(status_code=404, detail="Family not found")
            
        # Check access
        mem = self.db.execute(select(FamilyMember).where(FamilyMember.family_id == family_id, FamilyMember.person_id == person.id)).scalar_one_or_none()
        if not mem:
            raise HTTPException(status_code=404, detail="Family not found")
            
        fam = self.db.execute(select(Family).where(Family.id == family_id)).scalar_one()
        count = self.db.execute(select(func.count()).where(FamilyMember.family_id == fam.id)).scalar_one()
        
        # Use existing services bounded to this family
        # We need a way to filter events by family_id. event_service doesn't expose it directly but we can add or fetch manually.
        from app.db.models.event import Event, EventTarget
        from sqlalchemy import or_
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        stmt = select(Event).distinct().join(EventTarget, Event.id == EventTarget.event_id).where(
            EventTarget.family_id == family_id,
            Event.start_datetime >= now
        ).order_by(Event.start_datetime.asc()).limit(5)
        events = self.db.execute(stmt).scalars().all()
        
        activities, _ = self.activity_service.list_activities(user_id, family_id=family_id, limit=5)
        
        return FamilyOverviewResponse(
            id=fam.id,
            name=fam.name,
            member_count=count,
            upcoming_events=[EventResponse.model_validate(e) for e in events],
            recent_activity=[ActivityResponse.model_validate(a) for a in activities]
        )
