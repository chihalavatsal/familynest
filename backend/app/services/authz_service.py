import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.db.models.person import Person
from app.db.models.family import FamilyMember, ALLOWED_FAMILY_ROLES
from app.db.models.privacy import FamilyPrivacySettings
from app.db.models.memory import Memory, MemoryAllowedUser
from app.db.models.album import Album, AlbumAllowedUser
from app.db.models.media import Media

class AuthzService:
    def __init__(self, db: Session):
        self.db = db

    def get_family_member(self, user_id: uuid.UUID, family_id: uuid.UUID) -> Optional[FamilyMember]:
        # A User's family membership is defined by their claimed Person belonging to the Family.
        stmt = select(FamilyMember).join(Person, Person.id == FamilyMember.person_id).where(
            Person.claimed_by_user_id == user_id,
            FamilyMember.family_id == family_id
        )
        return self.db.execute(stmt).scalar_one_or_none()
        
    def get_family_settings(self, family_id: uuid.UUID) -> FamilyPrivacySettings:
        stmt = select(FamilyPrivacySettings).where(FamilyPrivacySettings.family_id == family_id)
        settings = self.db.execute(stmt).scalar_one_or_none()
        if not settings:
            settings = FamilyPrivacySettings(family_id=family_id)
            self.db.add(settings)
            self.db.flush()
        return settings

    def can_view_family(self, user_id: uuid.UUID, family_id: uuid.UUID) -> bool:
        member = self.get_family_member(user_id, family_id)
        return member is not None

    def can_manage_family_settings(self, user_id: uuid.UUID, family_id: uuid.UUID) -> bool:
        member = self.get_family_member(user_id, family_id)
        if not member: return False
        if member.role == "owner": return True
        # For admin, check settings
        if member.role == "admin":
            settings = self.get_family_settings(family_id)
            return settings.member_management_role == "admin"
        return False

    def can_add_member(self, user_id: uuid.UUID, family_id: uuid.UUID) -> bool:
        member = self.get_family_member(user_id, family_id)
        if not member: return False
        if member.role == "owner": return True
        settings = self.get_family_settings(family_id)
        role_hierarchy = {"owner": 3, "admin": 2, "member": 1, "invited": 0}
        user_level = role_hierarchy.get(member.role, 0)
        req_level = role_hierarchy.get(settings.member_invites_role, 3)
        return user_level >= req_level

    def can_remove_member(self, user_id: uuid.UUID, family_id: uuid.UUID, target_user_id: Optional[uuid.UUID], target_role: str) -> bool:
        if target_role == "owner":
            return False # Cannot remove owner
        if user_id == target_user_id:
            return True # Can remove self (leave family)
            
        member = self.get_family_member(user_id, family_id)
        if not member: return False
        if member.role == "owner": return True
        
        settings = self.get_family_settings(family_id)
        role_hierarchy = {"owner": 3, "admin": 2, "member": 1, "invited": 0}
        user_level = role_hierarchy.get(member.role, 0)
        req_level = role_hierarchy.get(settings.member_management_role, 3)
        return user_level >= req_level

    def can_change_member_role(self, user_id: uuid.UUID, family_id: uuid.UUID, target_user_id: uuid.UUID, new_role: str) -> bool:
        if new_role == "owner":
            return False # Owner transfer requires specific workflow
        if user_id == target_user_id:
            return False # Cannot promote/demote self
            
        member = self.get_family_member(user_id, family_id)
        if not member: return False
        if member.role == "owner": return True
        
        settings = self.get_family_settings(family_id)
        if member.role == "admin" and settings.member_management_role == "admin":
            # Admin can manage roles, but cannot create another owner (checked above) or demote owner
            target_member = self.get_family_member(target_user_id, family_id)
            if target_member and target_member.role == "owner":
                return False
            return True
        return False

    def can_view_memory(self, user_id: uuid.UUID, memory: Memory) -> bool:
        if not self.can_view_family(user_id, memory.family_id):
            return False
        if memory.visibility == "family":
            return True
        if memory.visibility == "selected_members":
            stmt = select(MemoryAllowedUser).where(MemoryAllowedUser.memory_id == memory.id, MemoryAllowedUser.user_id == user_id)
            return self.db.execute(stmt).scalar_one_or_none() is not None
        return False

    def can_view_album(self, user_id: uuid.UUID, album: Album) -> bool:
        if not self.can_view_family(user_id, album.family_id):
            return False
        if album.visibility == "family":
            return True
        if album.visibility == "selected_members":
            stmt = select(AlbumAllowedUser).where(AlbumAllowedUser.album_id == album.id, AlbumAllowedUser.user_id == user_id)
            return self.db.execute(stmt).scalar_one_or_none() is not None
        return False

    def can_view_media(self, user_id: uuid.UUID, media: Media) -> bool:
        return self.can_view_family(user_id, media.family_id)

    def require_family_view(self, user_id: uuid.UUID, family_id: uuid.UUID):
        if not self.can_view_family(user_id, family_id):
            raise HTTPException(status_code=403, detail="Not authorized to view this family")

    def require_memory_view(self, user_id: uuid.UUID, memory: Memory):
        if not self.can_view_memory(user_id, memory):
            raise HTTPException(status_code=403, detail="Not authorized to view this memory")

    def require_album_view(self, user_id: uuid.UUID, album: Album):
        if not self.can_view_album(user_id, album):
            raise HTTPException(status_code=403, detail="Not authorized to view this album")

    def can_read_person(self, user_id: uuid.UUID, person_id: uuid.UUID) -> bool:
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        
        # 1. Created by you or claimed by you
        person = self.db.execute(select(Person).where(Person.id == person_id)).scalar_one_or_none()
        if not person:
            return False
        if person.created_by_user_id == user_id or person.claimed_by_user_id == user_id:
            return True
            
        # 2. In a shared family
        # Find families the user is in
        user_fams = select(FamilyMember.family_id).where(FamilyMember.person_id.in_(
            select(Person.id).where(Person.claimed_by_user_id == user_id)
        ))
        
        # Check if person is in any of those families
        shared_fam = self.db.execute(
            select(FamilyMember).where(
                FamilyMember.person_id == person_id,
                FamilyMember.family_id.in_(user_fams)
            )
        ).first()
        
        if shared_fam:
            return True
            
        # Add fallback: what if user has not claimed a person but created the family?
        # A user in family is technically based on person_id in family.
        # So we just rely on that. If they are the creator of the person, we already caught it.
        
        return False

    def can_edit_person(self, user_id: uuid.UUID, person_id: uuid.UUID) -> bool:
        from app.db.models.person import Person
        person = self.db.execute(select(Person).where(Person.id == person_id)).scalar_one_or_none()
        if not person:
            return False
        # Claimed users can edit themselves
        if person.claimed_by_user_id == user_id:
            return True
        # Creators can edit unclaimed people they created
        if person.created_by_user_id == user_id and not person.claimed_by_user_id:
            return True
        return False

    def get_accessible_people(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        
        # People created or claimed by user
        q1 = select(Person.id).where((Person.created_by_user_id == user_id) | (Person.claimed_by_user_id == user_id))
        
        # People in shared families
        user_fams = select(FamilyMember.family_id).where(FamilyMember.person_id.in_(
            select(Person.id).where(Person.claimed_by_user_id == user_id)
        ))
        q2 = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(user_fams))
        
        ids1 = self.db.execute(q1).scalars().all()
        ids2 = self.db.execute(q2).scalars().all()
        
        return list(set(list(ids1) + list(ids2)))
