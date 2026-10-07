"""Family Repository: Data access layer for the Family Network domain.

All database queries for Family and FamilyMember records live here.

Access policy (Phase 4):
  A User can see a Family if:
    - They are the Family creator (created_by_user_id == user_id), OR
    - Their claimed Person is a member of that Family.

This is intentionally layered — future phases can add team/invite-based access
without changing the router or service interfaces.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import Session

from app.db.models.family import Family, FamilyMember
from app.db.models.person import Person

# Whitelist of fields permitted for ORDER BY on families
ALLOWED_SORT_FIELDS = {"name", "created_at", "updated_at"}
ALLOWED_SORT_DIRS = {"asc", "desc"}

# Maximum page sizes
MAX_PAGE_SIZE = 100


class FamilyRepository:
    """Data access layer for Family and FamilyMember entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Family — Create / Read / Update / Delete
    # ------------------------------------------------------------------

    def create_family(
        self,
        *,
        name: str,
        description: Optional[str],
        created_by_user_id: uuid.UUID,
    ) -> Family:
        """Insert a new Family row. Caller must flush/commit."""
        family = Family(
            name=name,
            description=description,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(family)
        self.db.flush()
        return family

    def get_by_id(self, family_id: uuid.UUID) -> Optional[Family]:
        """Fetch a Family by primary key (internal — no access check)."""
        stmt = select(Family).where(Family.id == family_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_accessible_by_id(
        self,
        family_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        claimed_person_id: Optional[uuid.UUID],
    ) -> Optional[Family]:
        """Fetch a Family only if the given user has access.

        Access: creator OR their claimed Person is a family member.
        Returns None (→ 404) for inaccessible or non-existent families.
        """
        # Build access subquery: is claimed_person a member?
        creator_cond = Family.created_by_user_id == user_id

        if claimed_person_id:
            member_subq = (
                select(FamilyMember.family_id)
                .where(FamilyMember.person_id == claimed_person_id)
                .scalar_subquery()
            )
            access_cond = or_(creator_cond, Family.id.in_(member_subq))
        else:
            access_cond = creator_cond

        stmt = select(Family).where(
            Family.id == family_id,
            access_cond,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_accessible(
        self,
        *,
        user_id: uuid.UUID,
        claimed_person_id: Optional[uuid.UUID],
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> tuple[list[Family], int]:
        """Return paginated families accessible to the user.

        Access = creator OR claimed Person is a member.
        """
        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "created_at"
        if sort_dir not in ALLOWED_SORT_DIRS:
            sort_dir = "desc"
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        page = max(page, 1)

        creator_cond = Family.created_by_user_id == user_id
        if claimed_person_id:
            member_subq = (
                select(FamilyMember.family_id)
                .where(FamilyMember.person_id == claimed_person_id)
                .scalar_subquery()
            )
            access_cond = or_(creator_cond, Family.id.in_(member_subq))
        else:
            access_cond = creator_cond

        if search:
            pattern = f"%{search}%"
            search_cond = or_(
                Family.name.ilike(pattern),
                Family.description.ilike(pattern),
            )
            combined = and_(access_cond, search_cond)
        else:
            combined = access_cond

        count_stmt = select(func.count()).select_from(Family).where(combined)
        total: int = self.db.execute(count_stmt).scalar_one()

        sort_col = getattr(Family, sort_by)
        order = sort_col.desc() if sort_dir == "desc" else sort_col.asc()

        data_stmt = (
            select(Family)
            .where(combined)
            .order_by(order)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.execute(data_stmt).scalars().all())
        return items, total

    def update_family(self, family: Family, *, update_data: dict) -> Family:
        """Apply partial update fields to a Family. Caller must commit."""
        for field, value in update_data.items():
            setattr(family, field, value)
        family.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return family

    def delete_family(self, family: Family) -> None:
        """Delete a Family row. CASCADE removes family_members rows.
        People, Relationships, and Users are untouched.
        """
        self.db.delete(family)
        self.db.flush()

    def count_members(self, family_id: uuid.UUID) -> int:
        """Count total members in a family (any role)."""
        stmt = select(func.count()).select_from(FamilyMember).where(
            FamilyMember.family_id == family_id
        )
        return self.db.execute(stmt).scalar_one()

    # ------------------------------------------------------------------
    # Family Members
    # ------------------------------------------------------------------

    def add_member(
        self,
        *,
        family_id: uuid.UUID,
        person_id: uuid.UUID,
        role: str,
    ) -> FamilyMember:
        """Insert a FamilyMember row. Caller must flush/commit.

        Raises IntegrityError if (family_id, person_id) already exists.
        """
        member = FamilyMember(
            family_id=family_id,
            person_id=person_id,
            role=role,
            joined_at=datetime.now(timezone.utc),
        )
        self.db.add(member)
        self.db.flush()
        return member

    def get_member(
        self, family_id: uuid.UUID, person_id: uuid.UUID
    ) -> Optional[FamilyMember]:
        """Fetch a specific FamilyMember by (family_id, person_id)."""
        stmt = select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.person_id == person_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_member_by_user_claimed_person(
        self, family_id: uuid.UUID, claimed_person_id: uuid.UUID
    ) -> Optional[FamilyMember]:
        """Check if the user's claimed Person is a member of this family."""
        return self.get_member(family_id, claimed_person_id)

    def list_members(
        self,
        family_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[tuple[FamilyMember, Person]], int]:
        """Return paginated (FamilyMember, Person) pairs for a family."""
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        page = max(page, 1)

        count_stmt = select(func.count()).select_from(FamilyMember).where(
            FamilyMember.family_id == family_id
        )
        total: int = self.db.execute(count_stmt).scalar_one()

        data_stmt = (
            select(FamilyMember, Person)
            .join(Person, FamilyMember.person_id == Person.id)
            .where(FamilyMember.family_id == family_id)
            .order_by(FamilyMember.joined_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(data_stmt).all()
        pairs = [(row[0], row[1]) for row in rows]
        return pairs, total

    def update_member_role(
        self, member: FamilyMember, *, new_role: str
    ) -> FamilyMember:
        """Update the role of a FamilyMember. Caller must commit."""
        member.role = new_role
        self.db.flush()
        return member

    def remove_member(self, member: FamilyMember) -> None:
        """Remove a FamilyMember row. Person is NOT deleted."""
        self.db.delete(member)
        self.db.flush()

    def get_user_role_in_family(
        self,
        family_id: uuid.UUID,
        claimed_person_id: Optional[uuid.UUID],
    ) -> Optional[str]:
        """Return the role of a user's claimed Person in a family, or None."""
        if claimed_person_id is None:
            return None
        member = self.get_member(family_id, claimed_person_id)
        return member.role if member else None

    def count_owners(self, family_id: uuid.UUID) -> int:
        """Count members with the 'owner' role in a family."""
        stmt = select(func.count()).select_from(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.role == "owner",
        )
        return self.db.execute(stmt).scalar_one()

    def count_members_bulk(self, family_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        from sqlalchemy import func
        stmt = select(FamilyMember.family_id, func.count(FamilyMember.person_id)).where(FamilyMember.family_id.in_(family_ids)).group_by(FamilyMember.family_id)
        result = self.db.execute(stmt).all()
        return {fam_id: count for fam_id, count in result}
