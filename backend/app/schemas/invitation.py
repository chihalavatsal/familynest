from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, EmailStr

InvitationStatus = Literal["pending", "accepted", "expired", "cancelled"]


class InvitationBase(BaseModel):
    family_id: Optional[UUID] = None
    person_id: UUID
    invited_email: Optional[EmailStr] = None
    invited_phone: Optional[str] = None
    status: InvitationStatus = "pending"
    expires_at: Optional[datetime] = None


class InvitationCreate(InvitationBase):
    pass


class InvitationResponse(InvitationBase):
    id: UUID
    invited_by_user_id: UUID
    invitation_token: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
