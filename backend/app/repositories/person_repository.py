"""Person Repository: Data access layer for the People domain.

All database queries for Person records live here.
The repository enforces Phase-3 creator-based access control:
  - A user can only access persons they created (created_by_user_id == user_id).
  - This is intentionally temporary; future phases will add family-network-based access.
"""
import uuid
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.db.models.person import Person
from app.db.models.family import FamilyMember

# Whitelist of fields permitted for ORDER BY
ALLOWED_SORT_FIELDS = {"first_name", "last_name", "created_at", "date_of_birth"}
ALLOWED_SORT_DIRS = {"asc", "desc"}

# Maximum page size a client may request
MAX_PAGE_SIZE = 100


class PersonRepository:
    """Data access layer for Person entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, *, created_by_user_id: uuid.UUID, data: dict) -> Person:
        """Insert a new Person row and return the persisted instance.

        Args:
            created_by_user_id: UUID of the authenticated user creating the record.
            data: Validated field dict from PersonCreate.model_dump(exclude_unset=True).

        Returns:
            The persisted Person ORM object (not yet committed — caller manages tx).
        """
        person = Person(
            created_by_user_id=created_by_user_id,
            **data,
        )
        self.db.add(person)
        self.db.flush()  # Populate person.id before audit log in same transaction
        return person

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, person_id: uuid.UUID) -> Optional[Person]:
        """Fetch a Person by primary key, regardless of creator (internal use)."""
        stmt = select(Person).where(Person.id == person_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_accessible_by_id(
        self, person_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Person]:
        """Fetch a Person only if the given user is the creator.

        Phase-3 access policy: creator-based only.
        Returns None (→ 404) for persons that exist but are not accessible.
        Privacy-preserving: callers must return 404, not 403.
        """
        stmt = select(Person).where(
            Person.id == person_id,
            Person.created_by_user_id == user_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_accessible(
        self,
        *,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> tuple[list[Person], int]:
        """Return a paginated list of Persons created by user_id.

        Args:
            user_id: Only return persons this user created.
            page: 1-indexed page number.
            page_size: Items per page (capped at MAX_PAGE_SIZE).
            search: Optional text to match against first_name, middle_name,
                    last_name, nickname (parameterized, SQL-injection safe).
            sort_by: Column name to sort by (whitelist-enforced).
            sort_dir: 'asc' or 'desc' (whitelist-enforced).

        Returns:
            Tuple of (items, total_count).
        """
        # Enforce whitelist guards (should be validated at schema level too)
        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "created_at"
        if sort_dir not in ALLOWED_SORT_DIRS:
            sort_dir = "desc"

        # Clamp page_size
        page_size = min(page_size, MAX_PAGE_SIZE)
        page_size = max(page_size, 1)
        page = max(page, 1)

        # Base filter: Shared Family Network Access
        subq_my_person = select(Person.id).where(Person.claimed_by_user_id == user_id).scalar_subquery()
        subq_my_families = select(FamilyMember.family_id).where(FamilyMember.person_id == subq_my_person).scalar_subquery()
        subq_shared_people = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(subq_my_families)).scalar_subquery()

        base_filter = or_(
            Person.created_by_user_id == user_id,
            Person.claimed_by_user_id == user_id,
            Person.id.in_(subq_shared_people)
        )

        # Optional search across name fields (parameterized — no f-string interpolation)
        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                Person.first_name.ilike(pattern),
                Person.middle_name.ilike(pattern),
                Person.last_name.ilike(pattern),
                Person.nickname.ilike(pattern),
            )
            combined_filter = base_filter & search_filter
        else:
            combined_filter = base_filter

        # Count query (efficient — no data loaded)
        count_stmt = select(func.count()).select_from(Person).where(combined_filter)
        total: int = self.db.execute(count_stmt).scalar_one()

        # Data query with sort + pagination
        sort_column = getattr(Person, sort_by)
        if sort_dir == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        offset = (page - 1) * page_size
        data_stmt = (
            select(Person)
            .where(combined_filter)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )
        items = list(self.db.execute(data_stmt).scalars().all())

        return items, total

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, person: Person, *, update_data: dict) -> Person:
        """Apply a dict of field updates to a Person instance.

        Caller must commit/flush after this call.
        Only fields present in update_data are modified (PATCH semantics).

        Args:
            person: The ORM Person instance to update.
            update_data: Dict of field name → new value (from exclude_unset=True).

        Returns:
            The mutated Person ORM object (not yet committed).
        """
        for field, value in update_data.items():
            setattr(person, field, value)
        self.db.flush()
        return person
