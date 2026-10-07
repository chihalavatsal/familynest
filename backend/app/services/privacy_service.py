import uuid
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.person import Person
from app.db.models.family import FamilyMember
from app.db.models.privacy import PersonPrivacySettings, FamilyPrivacySettings
from app.schemas.profile import PersonListItem

class PrivacyService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_user_family_ids(self, user_id: uuid.UUID) -> List[uuid.UUID]:
        person = self.db.execute(select(Person).where(Person.claimed_by_user_id == user_id)).scalar_one_or_none()
        if not person:
            return []
        return list(self.db.execute(select(FamilyMember.family_id).where(FamilyMember.person_id == person.id)).scalars().all())

    def resolve_safe_person(self, target_person: Person, viewer_user_id: uuid.UUID) -> PersonListItem:
        viewer_is_owner = target_person.claimed_by_user_id == viewer_user_id
        viewer_is_creator = target_person.created_by_user_id == viewer_user_id
        
        # If the viewer owns or created the profile, they see everything
        if viewer_is_owner or viewer_is_creator:
            return PersonListItem.model_validate(target_person)
            
        # Get privacy settings
        settings = self.db.execute(select(PersonPrivacySettings).where(PersonPrivacySettings.person_id == target_person.id)).scalar_one_or_none()
        
        # Default settings if none exist
        if not settings:
            settings = PersonPrivacySettings(phone_visibility="private", email_visibility="private", dob_visibility="private", bio_visibility="family")
            
        # Are they in the same family?
        viewer_family_ids = self.get_user_family_ids(viewer_user_id)
        target_family_ids = list(self.db.execute(select(FamilyMember.family_id).where(FamilyMember.person_id == target_person.id)).scalars().all())
        in_same_family = any(fid in target_family_ids for fid in viewer_family_ids)
        
        summary = PersonListItem.model_validate(target_person)
        
        # Apply redactions
        if settings.phone_visibility == "private":
            summary.phone = None
        elif settings.phone_visibility == "family" and not in_same_family:
            summary.phone = None
            
        if settings.email_visibility == "private":
            summary.email = None
        elif settings.email_visibility == "family" and not in_same_family:
            summary.email = None
            
        if settings.dob_visibility == "private":
            summary.date_of_birth = None
        elif settings.dob_visibility == "family" and not in_same_family:
            summary.date_of_birth = None
            
        if settings.bio_visibility == "private":
            summary.bio = None
        elif settings.bio_visibility == "family" and not in_same_family:
            summary.bio = None
            
        return summary
        
    def get_settings(self, person_id: uuid.UUID) -> PersonPrivacySettings:
        settings = self.db.execute(select(PersonPrivacySettings).where(PersonPrivacySettings.person_id == person_id)).scalar_one_or_none()
        if not settings:
            settings = PersonPrivacySettings(person_id=person_id)
            self.db.add(settings)
            self.db.flush()
        return settings

    def get_family_settings(self, family_id: uuid.UUID) -> FamilyPrivacySettings:
        settings = self.db.execute(select(FamilyPrivacySettings).where(FamilyPrivacySettings.family_id == family_id)).scalar_one_or_none()
        if not settings:
            settings = FamilyPrivacySettings(family_id=family_id)
            self.db.add(settings)
            self.db.flush()
        return settings

    def update_family_settings(self, family_id: uuid.UUID, data: dict) -> FamilyPrivacySettings:
        settings = self.get_family_settings(family_id)
        if "allow_member_discovery" in data:
            settings.allow_member_discovery = data["allow_member_discovery"]
        if "default_content_visibility" in data:
            settings.default_content_visibility = data["default_content_visibility"]
        if "member_invites_role" in data:
            settings.member_invites_role = data["member_invites_role"]
        if "member_management_role" in data:
            settings.member_management_role = data["member_management_role"]
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings
