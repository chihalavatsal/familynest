import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.person import PersonListItem

# We'll use simple string constants for types
INVITATION_TYPE_CLAIM = "person_claim"


class InvitationCreate(BaseModel):
    """Payload to create an invitation."""
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    invitation_type: str = Field(default=INVITATION_TYPE_CLAIM, description="Type of invitation")


class InvitationResponse(BaseModel):
    """Safe public representation of an invitation."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    family_id: Optional[uuid.UUID]
    person: PersonListItem
    invited_by_user_id: uuid.UUID
    invited_email: Optional[str]
    invited_phone: Optional[str]
    invitation_type: str
    status: str
    expires_at: Optional[datetime]
    created_at: datetime


class InvitationDetailResponse(InvitationResponse):
    """Detailed view might include the token ONLY immediately after creation."""
    invitation_token: Optional[str] = None


class InvitationListResponse(BaseModel):
    """Paginated list of invitations."""
    items: List[InvitationResponse]
    total: int


class PersonClaimResponse(BaseModel):
    """Response after successfully claiming a person."""
    model_config = ConfigDict(from_attributes=True)
    person: PersonListItem
    claimed: bool = True
