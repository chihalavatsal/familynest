"""Relationship API Router — Phase 5.

All endpoints require an authenticated Bearer access token.

Routes:
  POST   /api/v1/relationships
  GET    /api/v1/relationships
  GET    /api/v1/relationships/{id}
  PATCH  /api/v1/relationships/{id}
  DELETE /api/v1/relationships/{id}

Key rules:
  - No Family merges or automatic memberships are created here.
  - Identities (person_a, person_b) and types are immutable once created.
  - Symmetrical relationships (e.g., sibling, spouse) are handled correctly.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    RelationshipListResponse,
    RelationshipType,
)
from app.services.relationship_service import RelationshipService


router = APIRouter(prefix="/relationships", tags=["Relationships"])


@router.post(
    "",
    response_model=RelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Relationship",
    description=(
        "Connects two existing People. "
        "User must have legitimate access to both People. "
        "Will not create a duplicate active logical relationship."
    ),
)
def create_relationship(
    body: RelationshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelationshipResponse:
    return RelationshipService(db).create_relationship(data=body, current_user=current_user)


@router.get(
    "",
    response_model=RelationshipListResponse,
    status_code=status.HTTP_200_OK,
    summary="List accessible Relationships",
    description="Returns relationships involving at least one Person the User can access.",
)
def list_relationships(
    person_id: Optional[uuid.UUID] = Query(None, description="Filter by a specific person"),
    relationship_type: Optional[RelationshipType] = Query(None, description="Filter by relationship type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelationshipListResponse:
    return RelationshipService(db).list_relationships(
        current_user=current_user,
        person_id=person_id,
        relationship_type=relationship_type,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Relationship detail",
    description="Fetch full details. User must have access to at least one involved Person.",
)
def get_relationship(
    relationship_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelationshipResponse:
    return RelationshipService(db).get_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )


@router.patch(
    "/{relationship_id}",
    response_model=RelationshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Relationship status/dates",
    description=(
        "Modify dates or current status. "
        "Cannot change the People or the Relationship Type."
    ),
)
def update_relationship(
    relationship_id: uuid.UUID,
    body: RelationshipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelationshipResponse:
    return RelationshipService(db).update_relationship(
        relationship_id=relationship_id,
        data=body,
        current_user=current_user,
    )


@router.delete(
    "/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Relationship",
    description="Hard delete a relationship. Note: consider setting is_current=false via PATCH for divorces.",
)
def delete_relationship(
    relationship_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    RelationshipService(db).delete_relationship(
        relationship_id=relationship_id,
        current_user=current_user,
    )
