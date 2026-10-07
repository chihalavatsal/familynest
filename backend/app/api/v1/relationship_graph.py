"""Relationship Graph API Router — Phase 6.

Read-only endpoints for dynamically traversing and deriving relationships.
Never mutates the database.

Routes:
  GET /api/v1/relationships/how-related/{person_id}
  GET /api/v1/relationships/path/{person_id}
  GET /api/v1/people/{person_id}/relationships
  GET /api/v1/people/{person_id}/ancestors
  GET /api/v1/people/{person_id}/descendants
  GET /api/v1/people/{person_id}/siblings
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.relationship_graph import (
    KinshipResult,
    RelatedPersonListResponse,
)
from app.services.relationship_graph_service import RelationshipGraphService


# We define two routers to attach to their respective prefixes natively
relationships_router = APIRouter(prefix="/relationships", tags=["Relationships (Graph)"])
people_router = APIRouter(prefix="/people", tags=["People (Graph)"])


@relationships_router.get(
    "/how-related/{person_id}",
    response_model=KinshipResult,
    status_code=status.HTTP_200_OK,
    summary="How am I related?",
    description="Find the shortest relationship path between the current user's claimed Person and the target Person.",
)
def how_related(
    person_id: uuid.UUID,
    max_depth: int = Query(6, ge=1, le=12, description="Maximum traversal depth"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KinshipResult:
    return RelationshipGraphService(db).get_kinship(
        user_id=current_user.id,
        target_id=person_id,
        max_depth=max_depth,
    )


@relationships_router.get(
    "/path/{person_id}",
    response_model=KinshipResult,
    status_code=status.HTTP_200_OK,
    summary="Get Relationship Path",
    description="Identical behavior to how-related. Exists for strict requirement compliance.",
)
def relationship_path(
    person_id: uuid.UUID,
    max_depth: int = Query(6, ge=1, le=12, description="Maximum traversal depth"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KinshipResult:
    return RelationshipGraphService(db).get_kinship(
        user_id=current_user.id,
        target_id=person_id,
        max_depth=max_depth,
    )


@people_router.get(
    "/{person_id}/relationships",
    response_model=RelatedPersonListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Person Relationships",
    description="List all 1st-degree (direct) relationships for this Person.",
)
def person_direct_relationships(
    person_id: uuid.UUID,
    include_historical: bool = Query(False, description="Include divorced/historical edges"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelatedPersonListResponse:
    return RelationshipGraphService(db).get_direct_relationships(
        user_id=current_user.id,
        person_id=person_id,
        include_historical=include_historical,
    )


@people_router.get(
    "/{person_id}/ancestors",
    response_model=RelatedPersonListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Person Ancestors",
    description="Traverse upward to find all ancestors up to max_depth.",
)
def person_ancestors(
    person_id: uuid.UUID,
    max_depth: int = Query(6, ge=1, le=12, description="Maximum traversal depth"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelatedPersonListResponse:
    return RelationshipGraphService(db).get_ancestors(
        user_id=current_user.id,
        person_id=person_id,
        max_depth=max_depth,
    )


@people_router.get(
    "/{person_id}/descendants",
    response_model=RelatedPersonListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Person Descendants",
    description="Traverse downward to find all descendants up to max_depth.",
)
def person_descendants(
    person_id: uuid.UUID,
    max_depth: int = Query(6, ge=1, le=12, description="Maximum traversal depth"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelatedPersonListResponse:
    return RelationshipGraphService(db).get_descendants(
        user_id=current_user.id,
        person_id=person_id,
        max_depth=max_depth,
    )


@people_router.get(
    "/{person_id}/siblings",
    response_model=RelatedPersonListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Person Siblings",
    description="Find explicitly linked siblings AND siblings inferred through shared parents.",
)
def person_siblings(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RelatedPersonListResponse:
    return RelationshipGraphService(db).get_siblings(
        user_id=current_user.id,
        person_id=person_id,
    )
