"""People API Router — Phase 3 People Domain.

All endpoints require an authenticated Bearer access token.

Routes:
  POST   /api/v1/people          → Create a person (201)
  GET    /api/v1/people          → List accessible people (200, paginated)
  GET    /api/v1/people/{id}     → Get person detail (200)
  PATCH  /api/v1/people/{id}     → Partial update (200)

Design rules enforced here:
  - get_current_user() required on ALL routes.
  - created_by_user_id is always derived from current_user.id — never from request body.
  - claimed_by_user_id is NOT in any request schema.
  - Privacy-preserving 404 for inaccessible persons.
  - Thin routing layer — all business logic delegates to PersonService.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.person import (
    PersonCreate,
    PersonDetailResponse,
    PersonListResponse,
    PersonUpdate,
    ALLOWED_SORT_FIELDS,
    ALLOWED_SORT_DIRS,
)
from app.services.person_service import PersonService

router = APIRouter(prefix="/people", tags=["People"])


@router.post(
    "",
    response_model=PersonDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Person",
    description=(
        "Creates a canonical Person record. "
        "USER ≠ PERSON: this does NOT create a user account. "
        "The authenticated user becomes the creator; claimed_by_user_id is NOT set here."
    ),
)
def create_person(
    body: PersonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonDetailResponse:
    """Create a new Person.

    - `created_by_user_id` is always set to the authenticated user's id.
    - `claimed_by_user_id` is NOT set during creation.
    - `profile_status` defaults to `unclaimed`.
    """
    service = PersonService(db)
    return service.create_person(
        data=body,
        created_by_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=PersonListResponse,
    status_code=status.HTTP_200_OK,
    summary="List accessible people",
    description=(
        "Returns a paginated list of Persons created by the authenticated user. "
        "Sensitive fields (phone, email) are excluded from list results. "
        "Use GET /people/{id} to retrieve full detail including contact fields."
    ),
)
def list_people(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(
        None, min_length=1, max_length=100,
        description="Search first_name, middle_name, last_name, nickname"
    ),
    sort_by: str = Query(
        "created_at",
        description=f"Sort field. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}",
    ),
    sort_dir: str = Query(
        "desc",
        description="Sort direction: asc or desc",
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonListResponse:
    """List persons created by the authenticated user.

    Supports:
    - Pagination via `page` and `page_size`
    - Full-text search via `search` (first_name, middle_name, last_name, nickname)
    - Sorting via `sort_by` and `sort_dir`
    """
    # Sanitize sort params against whitelists (fail safe to defaults)
    safe_sort_by = sort_by if sort_by in ALLOWED_SORT_FIELDS else "created_at"
    safe_sort_dir = sort_dir if sort_dir in ALLOWED_SORT_DIRS else "desc"

    service = PersonService(db)
    return service.list_people(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=safe_sort_by,
        sort_dir=safe_sort_dir,
    )


@router.get(
    "/{person_id}",
    response_model=PersonDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Person detail",
    description=(
        "Returns full Person detail including sensitive fields (phone, email). "
        "Returns 404 if the person does not exist or is not accessible to the caller. "
        "This is intentionally privacy-preserving."
    ),
)
def get_person(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonDetailResponse:
    """Get a Person by ID (creator-only access in Phase 3)."""
    service = PersonService(db)
    return service.get_person(
        person_id=person_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{person_id}",
    response_model=PersonDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a Person",
    description=(
        "Applies a partial (PATCH) update to a Person record. "
        "Only fields included in the request body are modified. "
        "Returns 404 if person does not exist or is not accessible. "
        "Mutations are recorded in audit_logs."
    ),
)
def update_person(
    person_id: uuid.UUID,
    body: PersonUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonDetailResponse:
    """Partially update a Person (PATCH).

    - Omitted fields are NOT changed.
    - `claimed_by_user_id`, `created_by_user_id`, `id`, `created_at` are never modifiable.
    - Mutation is recorded in audit_logs.
    """
    service = PersonService(db)
    return service.update_person(
        person_id=person_id,
        data=body,
        user_id=current_user.id,
    )


from app.schemas.invitation import PersonClaimResponse, InvitationCreate, InvitationDetailResponse
from app.services.person_claim_service import PersonClaimService


@router.post(
    "/{person_id}/claim",
    response_model=PersonClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Claim a Person profile",
    description="Directly claim a person profile that you are authorized to access.",
)
def claim_person(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonClaimResponse:
    """Claim a canonical Person profile."""
    service = PersonClaimService(db)
    return service.claim_person(
        user_id=current_user.id,
        person_id=person_id,
    )


@router.post(
    "/{person_id}/invitations",
    response_model=InvitationDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an invitation for a Person",
    description="Create a secure invitation token to allow another user to claim this person.",
)
def create_person_invitation(
    person_id: uuid.UUID,
    invitation: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationDetailResponse:
    """Create a claim invitation for a Person."""
    service = PersonClaimService(db)
    return service.create_invitation(
        user_id=current_user.id,
        person_id=person_id,
        data=invitation,
    )


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Person",
)
def delete_person(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a person record. Only the person who created the profile can delete it.
    Cascades to relationships, employments, educations etc via DB constraints."""
    from app.db.models.person import Person
    from app.db.models.relationship import Relationship
    from app.db.models.employment import Employment
    from app.db.models.education import Education
    from fastapi import HTTPException
    from sqlalchemy import or_

    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Only the creator or the person's claimed user can delete
    if person.created_by_user_id != current_user.id and person.claimed_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this person")

    # Cannot delete your own claimed profile
    if person.claimed_by_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own profile. Update it instead.")

    # Delete related records first
    db.query(Relationship).filter(
        or_(Relationship.person_a_id == person_id, Relationship.person_b_id == person_id)
    ).delete(synchronize_session=False)

    db.query(Employment).filter(Employment.person_id == person_id).delete(synchronize_session=False)
    db.query(Education).filter(Education.person_id == person_id).delete(synchronize_session=False)

    db.delete(person)
    db.commit()
