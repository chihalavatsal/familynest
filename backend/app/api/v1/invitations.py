import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user, get_db
from app.db.models.user import User
from sqlalchemy.orm import Session

from app.schemas.invitation import (
    InvitationResponse,
    InvitationListResponse,
    PersonClaimResponse,
)
from app.services.person_claim_service import PersonClaimService

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.get(
    "",
    response_model=InvitationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Invitations",
)
def list_invitations(
    direction: Optional[str] = Query(None, description="'sent' or 'received'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationListResponse:
    service = PersonClaimService(db)
    return service.list_invitations(user_id=current_user.id, direction=direction)


@router.get(
    "/{invitation_id}",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Invitation Detail",
)
def get_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    service = PersonClaimService(db)
    return service.get_invitation(user_id=current_user.id, invitation_id=invitation_id)


@router.post(
    "/{invitation_id}/cancel",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel Invitation",
)
def cancel_invitation(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InvitationResponse:
    service = PersonClaimService(db)
    return service.cancel_invitation(user_id=current_user.id, invitation_id=invitation_id)


@router.post(
    "/{token}/accept",
    response_model=PersonClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Invitation",
)
def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonClaimResponse:
    service = PersonClaimService(db)
    return service.accept_invitation(user_id=current_user.id, raw_token=token)

@router.post(
    "/{invitation_id}/accept",
    response_model=PersonClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Invitation by ID",
)
def accept_invitation_by_id(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonClaimResponse:
    service = PersonClaimService(db)
    return service.accept_invitation_by_id(user_id=current_user.id, invitation_id=invitation_id)
