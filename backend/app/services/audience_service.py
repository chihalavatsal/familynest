import uuid
from typing import Set, List
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.family import FamilyMember
from app.db.models.person import Person
from app.schemas.notification import NotificationAudienceInput, AudienceType

class AudienceService:
    def __init__(self, db: Session):
        self.db = db

    def resolve_audience(self, creator_user_id: uuid.UUID, audience: NotificationAudienceInput) -> Set[uuid.UUID]:
        """Resolves audience to a set of User IDs and enforces authorization."""
        if audience.type == AudienceType.FAMILY:
            if not audience.family_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="family_id is required for family audience")
            return self._resolve_family(creator_user_id, audience.family_id)
            
        elif audience.type == AudienceType.SELECTED_MEMBERS:
            if not audience.person_ids:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="person_ids is required for selected_members audience")
            return self._resolve_selected_members(creator_user_id, audience.person_ids)
            
        elif audience.type == AudienceType.USER:
            return {creator_user_id}
            
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported audience type")

    def _resolve_family(self, creator_user_id: uuid.UUID, family_id: uuid.UUID) -> Set[uuid.UUID]:
        # Enforce authorization: creator must be owner or admin of the family
        # (Wait, what if a system process is creating the notification? For this phase, let's assume creator_user_id is the user).
        
        # Check creator's role
        creator_person = self.db.execute(select(Person).where(Person.claimed_by_user_id == creator_user_id)).scalar_one_or_none()
        if not creator_person:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creator does not have a claimed profile")
            
        member_stmt = select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.person_id == creator_person.id
        )
        creator_membership = self.db.execute(member_stmt).scalar_one_or_none()
        
        if not creator_membership or creator_membership.role not in ("owner", "admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to target this family audience")
            
        # Get all members of the family
        all_members = self.db.execute(select(FamilyMember).where(FamilyMember.family_id == family_id)).scalars().all()
        person_ids = [m.person_id for m in all_members]
        
        # Resolve to claimed users
        users_stmt = select(Person.claimed_by_user_id).where(
            Person.id.in_(person_ids),
            Person.claimed_by_user_id.is_not(None)
        )
        user_ids = self.db.execute(users_stmt).scalars().all()
        return set(user_ids)

    def _resolve_selected_members(self, creator_user_id: uuid.UUID, person_ids: List[uuid.UUID]) -> Set[uuid.UUID]:
        # Enforce authorization: creator must have access to all selected people.
        # A user has access if they created the person, claimed the person, or are in a shared family.
        
        creator_person = self.db.execute(select(Person).where(Person.claimed_by_user_id == creator_user_id)).scalar_one_or_none()
        creator_person_id = creator_person.id if creator_person else None
        
        # Get creator's families
        creator_family_ids = []
        if creator_person_id:
            cf_stmt = select(FamilyMember.family_id).where(FamilyMember.person_id == creator_person_id)
            creator_family_ids = self.db.execute(cf_stmt).scalars().all()
            
        # Fetch the requested people
        people = self.db.execute(select(Person).where(Person.id.in_(person_ids))).scalars().all()
        if len(people) != len(set(person_ids)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more selected people not found")
            
        recipient_user_ids = set()
        
        for person in people:
            # Check auth
            authorized = False
            if person.created_by_user_id == creator_user_id:
                authorized = True
            elif person.claimed_by_user_id == creator_user_id:
                authorized = True
            elif creator_family_ids:
                # Check if person is in any of creator's families
                shared = self.db.execute(
                    select(FamilyMember).where(
                        FamilyMember.person_id == person.id,
                        FamilyMember.family_id.in_(creator_family_ids)
                    )
                ).first()
                if shared:
                    authorized = True
                    
            if not authorized:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to target person {person.id}")
                
            if person.claimed_by_user_id:
                recipient_user_ids.add(person.claimed_by_user_id)
                
        return recipient_user_ids
