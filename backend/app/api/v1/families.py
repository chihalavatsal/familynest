"""Family API Router — Phase 4 Family Network & Membership Domain.

All endpoints require an authenticated Bearer access token.

Family routes:
  POST   /api/v1/families           → Create a family (201)
  GET    /api/v1/families           → List accessible families (200, paginated)
  GET    /api/v1/families/{id}      → Get family detail (200)
  PATCH  /api/v1/families/{id}      → Partial update (200, owner/admin)
  DELETE /api/v1/families/{id}      → Delete family (204, owner only)

Membership routes:
  POST   /api/v1/families/{id}/members                     → Add member (201)
  GET    /api/v1/families/{id}/members                     → List members (200)
  PATCH  /api/v1/families/{id}/members/{person_id}         → Update role (200)
  DELETE /api/v1/families/{id}/members/{person_id}         → Remove member (204)

Key design rules enforced here:
  - get_current_user() required on ALL routes.
  - created_by_user_id is always server-derived — never from request body.
  - Family membership NEVER creates a Relationship.
  - Family membership NEVER creates a Person.
  - Thin routing layer — all logic delegates to FamilyService.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.family import (
    FamilyCreate,
    FamilyUpdate,
    FamilyResponse,
    FamilyListResponse,
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    FamilyMemberListResponse,
    ALLOWED_SORT_FIELDS,
    ALLOWED_SORT_DIRS,
)
from app.services.family_service import FamilyService

router = APIRouter(prefix="/families", tags=["Families"])


# =============================================================================
# Family CRUD
# =============================================================================

@router.post(
    "",
    response_model=FamilyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Family",
    description=(
        "Creates a new Family network. "
        "The authenticated user becomes the creator (created_by_user_id). "
        "If the user has a claimed Person, that Person is added as 'owner'. "
        "No Person or Relationship is created automatically."
    ),
)
def create_family(
    body: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyResponse:
    return FamilyService(db).create_family(data=body, current_user=current_user)


@router.get(
    "",
    response_model=FamilyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List accessible families",
    description=(
        "Returns paginated families where the authenticated user is the creator, "
        "or their claimed Person is a member. Families are private by default."
    ),
)
def list_families(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    search: Optional[str] = Query(
        None, min_length=1, max_length=100,
        description="Search family name and description",
    ),
    sort_by: str = Query(
        "created_at",
        description=f"Sort field. Allowed: {', '.join(sorted(ALLOWED_SORT_FIELDS))}",
    ),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyListResponse:
    safe_sort_by = sort_by if sort_by in ALLOWED_SORT_FIELDS else "created_at"
    safe_sort_dir = sort_dir if sort_dir in ALLOWED_SORT_DIRS else "desc"
    return FamilyService(db).list_families(
        current_user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=safe_sort_by,
        sort_dir=safe_sort_dir,
    )


@router.get(
    "/{family_id}",
    response_model=FamilyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Family detail",
    description=(
        "Returns family detail. "
        "Returns 404 if family does not exist or user is not authorized."
    ),
)
def get_family(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyResponse:
    return FamilyService(db).get_family(
        family_id=family_id, current_user=current_user
    )


@router.patch(
    "/{family_id}",
    response_model=FamilyResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update a Family",
    description=(
        "Updates name and/or description. "
        "Requires owner or admin role. "
        "Protected fields (id, created_by_user_id, created_at, updated_at) cannot be changed."
    ),
)
def update_family(
    family_id: uuid.UUID,
    body: FamilyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyResponse:
    return FamilyService(db).update_family(
        family_id=family_id, data=body, current_user=current_user
    )


@router.delete(
    "/{family_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Family",
    description=(
        "Deletes a Family and its membership rows. "
        "Requires owner role. "
        "People, Relationships, and User accounts are NOT deleted."
    ),
)
def delete_family(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    FamilyService(db).delete_family(
        family_id=family_id, current_user=current_user
    )


# =============================================================================
# Family Membership
# =============================================================================

@router.post(
    "/{family_id}/members",
    response_model=FamilyMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a Person to a Family",
    description=(
        "Adds an existing Person to the Family. "
        "Requires owner or admin role. "
        "The Person must already exist (404 if not). "
        "Duplicate membership returns 409. "
        "No Relationship or new Person is created."
    ),
)
def add_member(
    family_id: uuid.UUID,
    body: FamilyMemberCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMemberResponse:
    return FamilyService(db).add_member(
        family_id=family_id, data=body, current_user=current_user
    )


@router.get(
    "/{family_id}/members",
    response_model=FamilyMemberListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Family members",
    description=(
        "Returns paginated members of the family. "
        "Safe Person fields only — no phone, email, or passwords. "
        "Requires family access (member, admin, or owner, or creator)."
    ),
)
def list_members(
    family_id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMemberListResponse:
    return FamilyService(db).list_members(
        family_id=family_id,
        current_user=current_user,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{family_id}/members/{person_id}",
    response_model=FamilyMemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a Family member's role",
    description=(
        "Updates the role of a Family member. "
        "Requires owner or admin role. "
        "Assigning 'owner' is not permitted — owner transfer is deferred to a future phase."
    ),
)
def update_member_role(
    family_id: uuid.UUID,
    person_id: uuid.UUID,
    body: FamilyMemberUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMemberResponse:
    return FamilyService(db).update_member_role(
        family_id=family_id,
        person_id=person_id,
        data=body,
        current_user=current_user,
    )


@router.delete(
    "/{family_id}/members/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a Person from a Family",
    description=(
        "Removes a Person's membership from the Family. "
        "Owner can remove anyone (except last owner). "
        "Admin can remove non-owner members. "
        "Members can remove themselves. "
        "Person, Relationships, and Users are NOT deleted."
    ),
)
def remove_member(
    family_id: uuid.UUID,
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    FamilyService(db).remove_member(
        family_id=family_id,
        person_id=person_id,
        current_user=current_user,
    )

from app.schemas.profile import FamilyPrivacySettingsResponse, FamilyPrivacySettingsUpdate
from app.services.privacy_service import PrivacyService
from app.services.authz_service import AuthzService

@router.get("/{family_id}/settings", response_model=FamilyPrivacySettingsResponse)
def get_family_settings(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    authz = AuthzService(db)
    if not authz.can_manage_family_settings(current_user.id, family_id):
        raise HTTPException(status_code=403, detail="Not authorized to view family settings.")
    privacy_svc = PrivacyService(db)
    return privacy_svc.get_family_settings(family_id)

@router.patch("/{family_id}/settings", response_model=FamilyPrivacySettingsResponse)
def update_family_settings(
    family_id: uuid.UUID,
    data: FamilyPrivacySettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    authz = AuthzService(db)
    if not authz.can_manage_family_settings(current_user.id, family_id):
        raise HTTPException(status_code=403, detail="Not authorized to manage family settings.")
    privacy_svc = PrivacyService(db)
    
    # Audit logging
    from app.db.models.audit_log import AuditLog
    db.add(AuditLog(actor_user_id=current_user.id, action="family.privacy.update", entity_type="family", entity_id=family_id))
    
    return privacy_svc.update_family_settings(family_id, data.model_dump(exclude_unset=True))
