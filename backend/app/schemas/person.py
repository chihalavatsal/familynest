from uuid import UUID
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

ProfileStatus = Literal["unclaimed", "invited", "claimed", "deceased"]


class PersonBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_deceased: bool = False
    is_minor: bool = False
    profile_status: ProfileStatus = "unclaimed"


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_deceased: Optional[bool] = None
    is_minor: Optional[bool] = None
    profile_status: Optional[ProfileStatus] = None


class PersonResponse(PersonBase):
    id: UUID
    claimed_by_user_id: Optional[UUID] = None
    created_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
