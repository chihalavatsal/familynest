import uuid
from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models.event import Event, EventTarget, EventParticipant
from app.db.models.audit_log import AuditLog
from app.schemas.event import EventCreate, EventUpdate, EventParticipantInput
from app.repositories.event_repository import EventRepository
from app.services.audience_service import AudienceService

class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = EventRepository(db)
        self.audience_service = AudienceService(db)

    def create_event(self, creator_user_id: uuid.UUID, data: EventCreate) -> Event:
        # Date validation
        if data.all_day:
            if not data.start_date or not data.end_date:
                raise HTTPException(status_code=422, detail="start_date and end_date required for all_day events")
            if data.end_date < data.start_date:
                raise HTTPException(status_code=422, detail="end_date cannot be before start_date")
        else:
            if not data.start_datetime or not data.end_datetime:
                raise HTTPException(status_code=422, detail="start_datetime and end_datetime required for non-all_day events")
            if data.end_datetime < data.start_datetime:
                raise HTTPException(status_code=422, detail="end_datetime cannot be before start_datetime")
                
        # Resolve audience targets using audience service for auth checks
        # Even though audience service returns user IDs, it performs the auth checks we need
        self.audience_service.resolve_audience(creator_user_id, data.audience)
        
        event = Event(
            event_type=data.event_type,
            title=data.title,
            description=data.description,
            start_datetime=data.start_datetime,
            end_datetime=data.end_datetime,
            start_date=data.start_date,
            end_date=data.end_date,
            all_day=data.all_day,
            person_id=data.person_id,
            created_by_user_id=creator_user_id
        )
        self.repo.create_event(event)
        
        # Create targets
        target_user_id = creator_user_id if data.audience.type == 'user' else data.audience.user_id
        target = EventTarget(
            event_id=event.id,
            audience_type=data.audience.type,
            family_id=data.audience.family_id,
            user_id=target_user_id
        )
        targets = [target]
        if data.audience.type == 'selected_members':
            targets = [EventTarget(event_id=event.id, audience_type='selected_members', person_id=pid) for pid in data.audience.person_ids]
            
        self.repo.add_targets(targets)
        
        # Audit
        self.db.add(AuditLog(
            actor_user_id=creator_user_id, action="event.create", entity_type="event", entity_id=event.id,
            metadata_={"event_type": data.event_type, "title": data.title}
        ))
        
        # Activity
        if data.audience.type != 'user':
            from app.db.models.activity import Activity
            act = Activity(
                activity_type=f"{data.event_type}.created",
                entity_type="event",
                entity_id=event.id,
                actor_user_id=creator_user_id,
                family_id=data.audience.family_id if data.audience.type == 'family' else None
            )
            self.db.add(act)
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def _get_user_context(self, user_id: uuid.UUID):
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        person = self.db.execute(select(Person).where(Person.claimed_by_user_id == user_id)).scalar_one_or_none()
        person_id = person.id if person else None
        family_ids = []
        if person_id:
            family_ids = self.db.execute(select(FamilyMember.family_id).where(FamilyMember.person_id == person_id)).scalars().all()
        return person_id, list(family_ids)

    def _can_access(self, event_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        person_id, family_ids = self._get_user_context(user_id)
        ev_tup = self.repo.get_event_with_targets(event_id)
        if not ev_tup:
            return False
        ev, tgts = ev_tup
        if ev.created_by_user_id == user_id:
            return True
        for t in tgts:
            if t.user_id == user_id: return True
            if t.person_id and t.person_id == person_id: return True
            if t.family_id and t.family_id in family_ids: return True
        return False

    def get_event(self, event_id: uuid.UUID, user_id: uuid.UUID) -> Event:
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
        return self.repo.get_event(event_id)

    def update_event(self, event_id: uuid.UUID, user_id: uuid.UUID, data: EventUpdate) -> Event:
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
            
        event = self.repo.get_event(event_id)
        if event.created_by_user_id != user_id:
            # Maybe admins of family could update? Let's just restrict to creator for simplicity, 
            # unless it's a family event and user is admin. But spec says "Do not allow arbitrary ownership transfer. User A creates, User B updates -> auth failure"
            raise HTTPException(status_code=403, detail="Not authorized to update this event")
            
        if data.title is not None: event.title = data.title
        if data.description is not None: event.description = data.description
        if data.all_day is not None: event.all_day = data.all_day
        if data.start_datetime is not None: event.start_datetime = data.start_datetime
        if data.end_datetime is not None: event.end_datetime = data.end_datetime
        if data.start_date is not None: event.start_date = data.start_date
        if data.end_date is not None: event.end_date = data.end_date
        if data.status is not None: event.status = data.status
        
        # Audience update
        if data.audience:
            self.audience_service.resolve_audience(user_id, data.audience)
            self.repo.delete_targets_for_event(event_id)
            if data.audience.type == 'selected_members':
                targets = [EventTarget(event_id=event.id, audience_type='selected_members', person_id=pid) for pid in data.audience.person_ids]
            else:
                target_user_id = user_id if data.audience.type == 'user' else data.audience.user_id
                targets = [EventTarget(event_id=event.id, audience_type=data.audience.type, family_id=data.audience.family_id, user_id=target_user_id)]
            self.repo.add_targets(targets)
            
        self.db.add(AuditLog(actor_user_id=user_id, action="event.update", entity_type="event", entity_id=event.id))
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: uuid.UUID, user_id: uuid.UUID):
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
        event = self.repo.get_event(event_id)
        if event.created_by_user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this event")
            
        self.repo.delete_event(event)
        self.db.add(AuditLog(actor_user_id=user_id, action="event.delete", entity_type="event", entity_id=event_id))
        self.db.commit()

    def list_events(self, user_id: uuid.UUID, limit: int = 20, offset: int = 0, event_type: str = None, upcoming: bool = False):
        person_id, family_ids = self._get_user_context(user_id)
        return self.repo.list_events(user_id, family_ids, person_id, limit, offset, event_type, upcoming)
        
    def add_participant(self, event_id: uuid.UUID, user_id: uuid.UUID, person_id: uuid.UUID, status: str = "invited") -> EventParticipant:
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Auth to person
        # AudienceService._resolve_selected_members already has the logic to check person access!
        from app.schemas.notification import NotificationAudienceInput
        self.audience_service.resolve_audience(user_id, NotificationAudienceInput(type="selected_members", person_ids=[person_id]))
        
        existing = self.repo.get_participant(event_id, person_id)
        if existing:
            raise HTTPException(status_code=400, detail="Participant already exists")
            
        p = EventParticipant(event_id=event_id, person_id=person_id, status=status)
        self.repo.add_participant(p)
        self.db.add(AuditLog(actor_user_id=user_id, action="event.participant.add", entity_type="event_participant", entity_id=p.id))
        self.db.commit()
        return p
        
    def list_participants(self, event_id: uuid.UUID, user_id: uuid.UUID, limit: int = 20, offset: int = 0):
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
        return self.repo.list_participants(event_id, limit, offset)
        
    def delete_participant(self, event_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID):
        if not self._can_access(event_id, user_id):
            raise HTTPException(status_code=404, detail="Event not found")
        p = self.repo.get_participant(event_id, person_id)
        if not p:
            raise HTTPException(status_code=404, detail="Participant not found")
        
        event = self.repo.get_event(event_id)
        if event.created_by_user_id != user_id:
            # Wait, can a participant remove themselves?
            # They would need to map their user_id to person_id.
            person_id_self, _ = self._get_user_context(user_id)
            if person_id != person_id_self:
                raise HTTPException(status_code=403, detail="Not authorized to remove participant")
        
        self.repo.delete_participant(p)
        self.db.add(AuditLog(actor_user_id=user_id, action="event.participant.remove", entity_type="event_participant", entity_id=p.id))
        self.db.commit()
