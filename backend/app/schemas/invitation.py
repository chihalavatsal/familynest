from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator
import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

InvitationStatus = Literal["pending", "accepted", "expired", "cancelled"]


class InvitationBase(BaseModel):
    family_id: Optional[UUID] = None
    person_id: UUID
    invited_email: Optional[str] = None
    invited_phone: Optional[str] = None
    status: InvitationStatus = "pending"
    expires_at: Optional[datetime] = None

    @field_validator("invited_email", mode="before")
    @classmethod
    def validate_invited_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip().lower()
            if v and not EMAIL_REGEX.match(v):
                raise ValueError("Invalid email format")
            return v or None
        return v


class InvitationCreate(InvitationBase):
    pass


class InvitationResponse(InvitationBase):
    id: UUID
    invited_by_user_id: UUID
    invitation_token: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
