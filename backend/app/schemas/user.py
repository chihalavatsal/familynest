from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserBase(BaseModel):
    email: str
    display_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip().lower()
            if not EMAIL_REGEX.match(v):
                raise ValueError("Invalid email format")
        return v


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
