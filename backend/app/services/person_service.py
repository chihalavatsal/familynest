from app.services.authz_service import AuthzService
"""Person Service: Business logic layer for the People domain.

Enforces:
- Creator-based access control (Phase 3 policy)
- Audit logging for create/update mutations
- Transactional integrity (person mutation + audit log in same commit)
- Privacy-preserving 404 for inaccessible records
"""
import uuid
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.person import Person
from app.db.models.audit_log import AuditLog
from app.repositories.person_repository import PersonRepository, MAX_PAGE_SIZE
from app.schemas.person import (
    PersonCreate,
    PersonUpdate,
    PersonDetailResponse,
    PersonListItem,
    PersonListResponse,
)


class PersonService:
    """Business logic for Person CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PersonRepository(db)

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create_person(
        self, *, data: PersonCreate, created_by_user_id: uuid.UUID
    ) -> PersonDetailResponse:
        """Create a new Person record, log to audit_logs, and commit in one transaction.

        Rules:
        - created_by_user_id is ALWAYS derived from the authenticated token — never client-provided.
        - claimed_by_user_id is NOT set here (future claiming workflow).
        - profile_status defaults to 'unclaimed' unless client explicitly passes another value.

        Returns:
            PersonDetailResponse for the created person.
        """
        person_data = data.model_dump(exclude_unset=False)  # include defaults

        try:
            # Persist the person (flush gives us the id)
            person = self.repo.create(
                created_by_user_id=created_by_user_id,
                data=person_data,
            )

            # Write audit log in the same transaction
            audit = AuditLog(
                actor_user_id=created_by_user_id,
                action="person.create",
                entity_type="person",
                entity_id=person.id,
                metadata_={
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                    "profile_status": person.profile_status,
                },
            )
            self.db.add(audit)

            self.db.commit()
            self.db.refresh(person)
        except Exception:
            self.db.rollback()
            raise

        return PersonDetailResponse.model_validate(person)

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_people(
        self,
        *,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PersonListResponse:
        """Return a paginated list of People accessible to the authenticated user.

        Only persons the user created are returned (Phase 3 creator-based policy).

        Args:
            user_id: The authenticated user's UUID.
            page: 1-indexed page number.
            page_size: Items per page (max enforced by repository).
            search: Optional search string.
            sort_by: Sort column (whitelist-enforced in repository).
            sort_dir: 'asc' or 'desc'.

        Returns:
            PersonListResponse with items, pagination metadata.
        """
        clamped_page_size = min(page_size, MAX_PAGE_SIZE)
        items, total = self.repo.list_accessible(
            user_id=user_id,
            page=page,
            page_size=clamped_page_size,
            search=search,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        return PersonListResponse(
            items=[PersonListItem.model_validate(p) for p in items],
            page=page,
            page_size=clamped_page_size,
            total=total,
        )

    # ------------------------------------------------------------------
    # Get Detail
    # ------------------------------------------------------------------

    def get_person(
        self, *, person_id: uuid.UUID, user_id: uuid.UUID
    ) -> PersonDetailResponse:
        """Return full Person detail for the authenticated user.

        Returns 404 if the person does not exist OR is not accessible to this user.
        This is intentionally privacy-preserving (do not leak existence).
        """
        authz = AuthzService(self.db)
        if not authz.can_read_person(user_id, person_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )
        
        person = self.repo.get_by_id(person_id)
        return PersonDetailResponse.model_validate(person)

    # ------------------------------------------------------------------
    # Update (PATCH)
    # ------------------------------------------------------------------

    def update_person(
        self,
        *,
        person_id: uuid.UUID,
        data: PersonUpdate,
        user_id: uuid.UUID,
    ) -> PersonDetailResponse:
        """Partially update a Person record, log to audit_logs, and commit.

        Rules:
        - Privacy-preserving 404 if person doesn't exist or isn't accessible.
        - Only fields explicitly provided in the request body are modified.
        - claimed_by_user_id is NEVER touched here.
        - Audit log records the changed fields.

        Returns:
            PersonDetailResponse reflecting the updated person.
        """
        person = self.repo.get_accessible_by_id(person_id, user_id)
        if person is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            # Nothing to update — return current state
            return PersonDetailResponse.model_validate(person)

        try:
            # Capture which fields changed for audit record
            changed_fields = {
                field: {"from": getattr(person, field), "to": value}
                for field, value in update_dict.items()
            }

            # Apply the partial update (flush, no commit yet)
            person = self.repo.update(person, update_data=update_dict)

            # Manually bump updated_at (SQLAlchemy onupdate fires on flush/commit)
            person.updated_at = datetime.now(timezone.utc)

            # Write audit log in the same transaction
            audit = AuditLog(
                actor_user_id=user_id,
                action="person.update",
                entity_type="person",
                entity_id=person.id,
                metadata_={"changed_fields": list(changed_fields.keys())},
            )
            self.db.add(audit)

            self.db.commit()
            self.db.refresh(person)
        except HTTPException:
            raise
        except Exception:
            self.db.rollback()
            raise

        return PersonDetailResponse.model_validate(person)
