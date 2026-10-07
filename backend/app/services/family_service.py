"""Family Service: Business logic for the Family Network & Membership domain.

Architecture:
  Router → FamilyService → FamilyRepository → SQLAlchemy → Neon PostgreSQL

Authorization model (Phase 4):
  - Family visibility:  creator OR claimed Person is a member
  - Family update:      owner OR admin member (via claimed Person)
  - Family delete:      owner only (via claimed Person or creator)
  - Add/remove member:  owner OR admin
  - Update member role: owner OR admin (cannot assign 'owner')
  - List members:       any Family member (or creator)

USER ≠ PERSON invariant is maintained throughout:
  - We never create a Person from a User.
  - We look up the User's claimed Person (people.claimed_by_user_id == user.id).
  - If no claimed Person exists, the User can still create a Family but
    won't have a Person membership row.
"""
import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.audit_log import AuditLog
from app.db.models.family import Family, FamilyMember
from app.repositories.family_repository import FamilyRepository, MAX_PAGE_SIZE
from app.repositories.person_repository import PersonRepository
from app.schemas.family import (
    FamilyCreate,
    FamilyUpdate,
    FamilyResponse,
    FamilyListItem,
    FamilyListResponse,
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    FamilyMemberListResponse,
    ADMIN_ROLES,
    OWNER_ONLY_ROLES,
)


def _get_claimed_person(db: Session, user_id: uuid.UUID) -> Optional[Person]:
    """Find the Person record claimed by this user, if any.

    Uses PersonRepository's internal get_by_id after finding the claimed person.
    We query people.claimed_by_user_id directly to avoid cross-domain coupling.
    """
    from sqlalchemy import select
    stmt = select(Person).where(Person.claimed_by_user_id == user_id)
    return db.execute(stmt).scalar_one_or_none()


def _build_family_response(family: Family, member_count: int) -> FamilyResponse:
    return FamilyResponse(
        id=family.id,
        name=family.name,
        description=family.description,
        created_by_user_id=family.created_by_user_id,
        created_at=family.created_at,
        updated_at=family.updated_at,
        member_count=member_count,
    )


def _build_family_list_item(family: Family, member_count: int) -> FamilyListItem:
    return FamilyListItem(
        id=family.id,
        name=family.name,
        description=family.description,
        created_by_user_id=family.created_by_user_id,
        created_at=family.created_at,
        updated_at=family.updated_at,
        member_count=member_count,
    )


def _build_member_response(member: FamilyMember, person: Person) -> FamilyMemberResponse:
    return FamilyMemberResponse(
        person_id=member.person_id,
        family_id=member.family_id,
        role=member.role,
        joined_at=member.joined_at,
        created_at=member.created_at,
        first_name=person.first_name,
        last_name=person.last_name,
        nickname=person.nickname,
        profile_photo_url=person.profile_photo_url,
        profile_status=person.profile_status,
    )


class FamilyService:
    """Business logic for Family and FamilyMember operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = FamilyRepository(db)

    # ------------------------------------------------------------------
    # Internal authorization helpers
    # ------------------------------------------------------------------

    def _get_user_role(
        self,
        family_id: uuid.UUID,
        claimed_person_id: Optional[uuid.UUID],
        is_creator: bool,
    ) -> Optional[str]:
        """Return the effective role of a user in a family.

        A user is considered 'owner' if they are the family creator AND
        their claimed Person has an 'owner' membership row, or if we treat
        creator status itself (no claimed person) as implicit ownership for
        permission purposes.
        """
        if claimed_person_id:
            role = self.repo.get_user_role_in_family(family_id, claimed_person_id)
            if role:
                return role
        # If the user is the creator but has no person membership yet,
        # grant implicit creator privilege for permission checks.
        if is_creator:
            return "owner"
        return None

    def _require_access(
        self,
        family: Optional[Family],
        user: User,
        claimed_person_id: Optional[uuid.UUID],
        *,
        required_roles: set,
        privacy_preserving: bool = True,
    ) -> str:
        """Check that user has sufficient role; raise 404/403 otherwise.

        Returns the effective role string.
        """
        if family is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found",
            )
        is_creator = (family.created_by_user_id == user.id)
        effective_role = self._get_user_role(
            family.id, claimed_person_id, is_creator=is_creator
        )
        if effective_role is None:
            # User has no access — privacy-preserving 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found",
            )
        if effective_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_roles}",
            )
        return effective_role

    def _get_accessible_family_or_404(
        self,
        family_id: uuid.UUID,
        user: User,
        claimed_person_id: Optional[uuid.UUID],
    ) -> Family:
        """Fetch a family the user can access, or raise privacy-preserving 404."""
        family = self.repo.get_accessible_by_id(
            family_id,
            user_id=user.id,
            claimed_person_id=claimed_person_id,
        )
        if family is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found",
            )
        return family

    def _write_audit(
        self,
        *,
        actor_user_id: uuid.UUID,
        action: str,
        entity_type: str,
        entity_id: uuid.UUID,
        metadata: Optional[dict] = None,
    ) -> None:
        audit = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_=metadata or {},
        )
        self.db.add(audit)

    # ------------------------------------------------------------------
    # Family CRUD
    # ------------------------------------------------------------------

    def create_family(
        self,
        *,
        data: FamilyCreate,
        current_user: User,
    ) -> FamilyResponse:
        """Create a Family, optionally adding claimed Person as owner.

        Atomic transaction:
          1. Create Family row.
          2. If user has a claimed Person, add them as 'owner'.
          3. Write audit log.
          4. Commit.

        If user has no claimed Person, Family is created without any member rows.
        No Person is created automatically.
        No Relationship is created.
        """
        claimed_person = _get_claimed_person(self.db, current_user.id)

        try:
            family = self.repo.create_family(
                name=data.name,
                description=data.description,
                created_by_user_id=current_user.id,
            )

            if claimed_person:
                self.repo.add_member(
                    family_id=family.id,
                    person_id=claimed_person.id,
                    role="owner",
                )

            self._write_audit(
                actor_user_id=current_user.id,
                action="family.create",
                entity_type="family",
                entity_id=family.id,
                metadata={
                    "name": family.name,
                    "has_owner_member": claimed_person is not None,
                },
            )

            self.db.commit()
            self.db.refresh(family)
        except Exception:
            self.db.rollback()
            raise

        member_count = self.repo.count_members(family.id)
        return _build_family_response(family, member_count)

    def list_families(
        self,
        *,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> FamilyListResponse:
        """Return paginated families accessible to the user."""
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        clamped = min(page_size, MAX_PAGE_SIZE)
        families, total = self.repo.list_accessible(
            user_id=current_user.id,
            claimed_person_id=claimed_person_id,
            page=page,
            page_size=clamped,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

        items = []
        counts = self.repo.count_members_bulk([f.id for f in families])
        for family in families:
            count = counts.get(family.id, 0)
            items.append(_build_family_list_item(family, count))

        return FamilyListResponse(
            items=items,
            page=page,
            page_size=clamped,
            total=total,
        )

    def get_family(
        self,
        *,
        family_id: uuid.UUID,
        current_user: User,
    ) -> FamilyResponse:
        """Return full Family detail for an authorized user."""
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        count = self.repo.count_members(family.id)
        return _build_family_response(family, count)

    def update_family(
        self,
        *,
        family_id: uuid.UUID,
        data: FamilyUpdate,
        current_user: User,
    ) -> FamilyResponse:
        """Partially update a Family (owner or admin only)."""
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        is_creator = (family.created_by_user_id == current_user.id)
        effective_role = self._get_user_role(family.id, claimed_person_id, is_creator)

        if effective_role not in ADMIN_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only family owners and admins can update family details",
            )

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            count = self.repo.count_members(family.id)
            return _build_family_response(family, count)

        try:
            family = self.repo.update_family(family, update_data=update_dict)
            self._write_audit(
                actor_user_id=current_user.id,
                action="family.update",
                entity_type="family",
                entity_id=family.id,
                metadata={"changed_fields": list(update_dict.keys())},
            )
            self.db.commit()
            self.db.refresh(family)
        except Exception:
            self.db.rollback()
            raise

        count = self.repo.count_members(family.id)
        return _build_family_response(family, count)

    def delete_family(
        self,
        *,
        family_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """Delete a Family (owner only).

        CASCADE removes family_members rows.
        People, Relationships, and User accounts are untouched.
        """
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        is_creator = (family.created_by_user_id == current_user.id)
        effective_role = self._get_user_role(family.id, claimed_person_id, is_creator)

        if effective_role not in OWNER_ONLY_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the family owner can delete a family",
            )

        try:
            self._write_audit(
                actor_user_id=current_user.id,
                action="family.delete",
                entity_type="family",
                entity_id=family.id,
                metadata={"name": family.name},
            )
            self.repo.delete_family(family)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # ------------------------------------------------------------------
    # Family Membership
    # ------------------------------------------------------------------

    def add_member(
        self,
        *,
        family_id: uuid.UUID,
        data: FamilyMemberCreate,
        current_user: User,
    ) -> FamilyMemberResponse:
        """Add a Person to a Family (owner or admin only).

        Rules:
        - The Person must already exist (404 if not).
        - Duplicate membership raises 409.
        - No Person is created.
        - No Relationship is created.
        """
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        is_creator = (family.created_by_user_id == current_user.id)
        effective_role = self._get_user_role(family.id, claimed_person_id, is_creator)

        if effective_role not in ADMIN_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only family owners and admins can add members",
            )

        # Verify the target Person exists
        from sqlalchemy import select as sa_select
        from app.db.models.person import Person as PersonModel
        person_stmt = sa_select(PersonModel).where(PersonModel.id == data.person_id)
        person = self.db.execute(person_stmt).scalar_one_or_none()
        if person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        try:
            member = self.repo.add_member(
                family_id=family.id,
                person_id=data.person_id,
                role=data.role,
            )
            self._write_audit(
                actor_user_id=current_user.id,
                action="family.member.add",
                entity_type="family_member",
                entity_id=family.id,
                metadata={
                    "person_id": str(data.person_id),
                    "role": data.role,
                },
            )
            self.db.commit()
            self.db.refresh(member)
            self.db.refresh(person)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Person is already a member of this family",
            )
        except Exception:
            self.db.rollback()
            raise

        return _build_member_response(member, person)

    def list_members(
        self,
        *,
        family_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> FamilyMemberListResponse:
        """List members of a Family (any authorized family member or creator)."""
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )

        clamped = min(page_size, MAX_PAGE_SIZE)
        pairs, total = self.repo.list_members(family.id, page=page, page_size=clamped)

        return FamilyMemberListResponse(
            items=[_build_member_response(m, p) for m, p in pairs],
            page=page,
            page_size=clamped,
            total=total,
        )

    def update_member_role(
        self,
        *,
        family_id: uuid.UUID,
        person_id: uuid.UUID,
        data: FamilyMemberUpdate,
        current_user: User,
    ) -> FamilyMemberResponse:
        """Update the role of a family member (owner or admin only).

        Assigning 'owner' is blocked — owner transfer deferred to future phase.
        """
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        is_creator = (family.created_by_user_id == current_user.id)
        effective_role = self._get_user_role(family.id, claimed_person_id, is_creator)

        if effective_role not in ADMIN_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only family owners and admins can update member roles",
            )

        member = self.repo.get_member(family.id, person_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found",
            )

        # Prevent any role update on the owner's membership (protect ownership)
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change the role of the family owner",
            )

        # Get the Person for the response
        from sqlalchemy import select as sa_select
        from app.db.models.person import Person as PersonModel
        person_stmt = sa_select(PersonModel).where(PersonModel.id == person_id)
        person = self.db.execute(person_stmt).scalar_one_or_none()
        if person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        try:
            member = self.repo.update_member_role(member, new_role=data.role)
            self._write_audit(
                actor_user_id=current_user.id,
                action="family.member.update",
                entity_type="family_member",
                entity_id=family.id,
                metadata={
                    "person_id": str(person_id),
                    "new_role": data.role,
                },
            )
            self.db.commit()
            self.db.refresh(member)
        except Exception:
            self.db.rollback()
            raise

        return _build_member_response(member, person)

    def remove_member(
        self,
        *,
        family_id: uuid.UUID,
        person_id: uuid.UUID,
        current_user: User,
    ) -> None:
        """Remove a Person from a Family.

        Permissions:
        - owner can remove anyone (except themselves if last owner)
        - admin can remove normal members (not owner)
        - member can remove themselves (self-removal)

        Removing a member does NOT delete the Person, Relationships, or Users.
        """
        claimed_person = _get_claimed_person(self.db, current_user.id)
        claimed_person_id = claimed_person.id if claimed_person else None

        family = self._get_accessible_family_or_404(
            family_id, current_user, claimed_person_id
        )
        is_creator = (family.created_by_user_id == current_user.id)
        effective_role = self._get_user_role(family.id, claimed_person_id, is_creator)

        if effective_role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No access to this family",
            )

        member = self.repo.get_member(family.id, person_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found",
            )

        is_self_removal = (
            claimed_person_id is not None and claimed_person_id == person_id
        )

        # Permission rules:
        if not is_self_removal:
            # Only owner/admin can remove others
            if effective_role not in ADMIN_ROLES:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only family owners and admins can remove other members",
                )
            # Admin cannot remove owner
            if member.role == "owner" and effective_role == "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admins cannot remove the family owner",
                )

        # Prevent removing the last owner (family would have no owner)
        if member.role == "owner":
            owner_count = self.repo.count_owners(family.id)
            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot remove the last owner of a family. Transfer ownership first.",
                )

        try:
            self._write_audit(
                actor_user_id=current_user.id,
                action="family.member.remove",
                entity_type="family_member",
                entity_id=family.id,
                metadata={
                    "person_id": str(person_id),
                    "removed_role": member.role,
                    "self_removal": is_self_removal,
                },
            )
            self.repo.remove_member(member)
            self.db.commit()
        except HTTPException:
            raise
        except Exception:
            self.db.rollback()
            raise
