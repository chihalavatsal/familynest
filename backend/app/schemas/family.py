from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

FamilyRole = Literal["owner", "admin", "member", "invited"]


class FamilyBase(BaseModel):
    name: str
    description: Optional[str] = None


class FamilyCreate(FamilyBase):
    pass


class FamilyResponse(FamilyBase):
    id: UUID
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FamilyMemberBase(BaseModel):
    family_id: UUID
    person_id: UUID
    role: FamilyRole = "member"


class FamilyMemberCreate(FamilyMemberBase):
    pass


class FamilyMemberResponse(FamilyMemberBase):
    id: UUID
    joined_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
