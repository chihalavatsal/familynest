"""Person schemas for FamilyNest People Domain API (Phase 3).

Design rules:
- USER ≠ PERSON: Person is a canonical human identity, not an auth account.
- claimed_by_user_id is NEVER client-writable (future claiming workflow only).
- id, created_by_user_id, created_at, updated_at are NEVER client-writable.
- phone and email are omitted from list responses (privacy).
- profile_status defaults to 'unclaimed'; clients may override during creation.
"""
import re
from uuid import UUID
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# Valid profile_status values (mirrors DB CHECK constraint)
ProfileStatus = Literal["unclaimed", "invited", "claimed", "deceased"]

# Valid sort fields whitelist
ALLOWED_SORT_FIELDS = {"first_name", "last_name", "created_at", "date_of_birth"}

# Valid sort directions
ALLOWED_SORT_DIRS = {"asc", "desc"}

# Simple email regex (email-validator package not installed)
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Field length limits
MAX_NAME_LENGTH = 100
MAX_PLACE_LENGTH = 255
MAX_PHONE_LENGTH = 50
MAX_EMAIL_LENGTH = 255
MAX_BIO_LENGTH = 5000


class PersonCreate(BaseModel):
    """Fields a client may supply when creating a Person.

    Excluded from client input:
    - id (server-generated UUID)
    - created_by_user_id (server-derived from auth token)
    - claimed_by_user_id (future claiming workflow only)
    - created_at / updated_at (server timestamps)
    """

    # Required
    first_name: str

    # Optional identity fields
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None

    # Dates
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None

    # Location
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    current_city: Optional[str] = None

    # Professional / narrative
    occupation: Optional[str] = None
    bio: Optional[str] = None

    # Media
    profile_photo_url: Optional[str] = None

    # Contact (stored but excluded from list responses)
    phone: Optional[str] = None
    email: Optional[str] = None

    # Status flags
    is_deceased: bool = False
    is_minor: bool = False
    profile_status: ProfileStatus = "unclaimed"

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("first_name must not be empty or whitespace")
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"first_name must be at most {MAX_NAME_LENGTH} characters")
        return v

    @field_validator("middle_name", "last_name", "nickname", mode="before")
    @classmethod
    def strip_optional_names(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"Name fields must be at most {MAX_NAME_LENGTH} characters")
        return v or None  # convert empty string to None

    @field_validator("birth_place", "death_place", "current_city", mode="before")
    @classmethod
    def strip_place_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PLACE_LENGTH:
            raise ValueError(f"Place fields must be at most {MAX_PLACE_LENGTH} characters")
        return v or None

    @field_validator("occupation", mode="before")
    @classmethod
    def strip_occupation(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PLACE_LENGTH:
            raise ValueError(f"occupation must be at most {MAX_PLACE_LENGTH} characters")
        return v or None

    @field_validator("bio", mode="before")
    @classmethod
    def strip_bio(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_BIO_LENGTH:
            raise ValueError(f"bio must be at most {MAX_BIO_LENGTH} characters")
        return v or None

    @field_validator("phone", mode="before")
    @classmethod
    def strip_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PHONE_LENGTH:
            raise ValueError(f"phone must be at most {MAX_PHONE_LENGTH} characters")
        return v or None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        if len(v) > MAX_EMAIL_LENGTH:
            raise ValueError(f"email must be at most {MAX_EMAIL_LENGTH} characters")
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("gender", mode="before")
    @classmethod
    def strip_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def validate_dates(self) -> "PersonCreate":
        today = date.today()

        if self.date_of_birth is not None and self.date_of_birth > today:
            raise ValueError("date_of_birth cannot be in the future")

        if self.date_of_death is not None:
            if self.date_of_death > today:
                raise ValueError("date_of_death cannot be in the future")
            if self.date_of_birth is not None and self.date_of_death < self.date_of_birth:
                raise ValueError("date_of_death cannot be before date_of_birth")

        return self


class PersonUpdate(BaseModel):
    """Fields a client may supply for a partial (PATCH) update of a Person.

    All fields are Optional. Unset fields are NOT modified.
    Use model_dump(exclude_unset=True) to get only the changed fields.
    """

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_deceased: Optional[bool] = None
    is_minor: Optional[bool] = None
    profile_status: Optional[ProfileStatus] = None

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("first_name must not be empty or whitespace")
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"first_name must be at most {MAX_NAME_LENGTH} characters")
        return v

    @field_validator("middle_name", "last_name", "nickname", mode="before")
    @classmethod
    def strip_optional_names(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"Name fields must be at most {MAX_NAME_LENGTH} characters")
        return v or None

    @field_validator("birth_place", "death_place", "current_city", mode="before")
    @classmethod
    def strip_place_fields(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PLACE_LENGTH:
            raise ValueError(f"Place fields must be at most {MAX_PLACE_LENGTH} characters")
        return v or None

    @field_validator("occupation", mode="before")
    @classmethod
    def strip_occupation(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PLACE_LENGTH:
            raise ValueError(f"occupation must be at most {MAX_PLACE_LENGTH} characters")
        return v or None

    @field_validator("bio", mode="before")
    @classmethod
    def strip_bio(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_BIO_LENGTH:
            raise ValueError(f"bio must be at most {MAX_BIO_LENGTH} characters")
        return v or None

    @field_validator("phone", mode="before")
    @classmethod
    def strip_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_PHONE_LENGTH:
            raise ValueError(f"phone must be at most {MAX_PHONE_LENGTH} characters")
        return v or None

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        if len(v) > MAX_EMAIL_LENGTH:
            raise ValueError(f"email must be at most {MAX_EMAIL_LENGTH} characters")
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("gender", mode="before")
    @classmethod
    def strip_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        return v or None

    @model_validator(mode="after")
    def validate_dates(self) -> "PersonUpdate":
        today = date.today()

        if self.date_of_birth is not None and self.date_of_birth > today:
            raise ValueError("date_of_birth cannot be in the future")

        if self.date_of_death is not None:
            if self.date_of_death > today:
                raise ValueError("date_of_death cannot be in the future")
            if self.date_of_birth is not None and self.date_of_death < self.date_of_birth:
                raise ValueError("date_of_death cannot be before date_of_birth")

        return self


class PersonListItem(BaseModel):
    """Summary representation of a Person for paginated list responses.

    Privacy: phone and email are intentionally excluded from list responses.
    They are only available in the full detail (PersonDetailResponse).
    """

    id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_deceased: bool
    is_minor: bool
    profile_status: str
    profile_photo_url: Optional[str] = None
    occupation: Optional[str] = None
    current_city: Optional[str] = None
    created_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonDetailResponse(BaseModel):
    """Full detail representation of a Person (for authenticated detail endpoint).

    Includes sensitive contact fields (phone, email) that are excluded from list.
    """

    id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    death_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_deceased: bool
    is_minor: bool
    profile_status: str

    # Server-managed fields (read-only)
    created_by_user_id: Optional[UUID] = None
    claimed_by_user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonListResponse(BaseModel):
    """Paginated response wrapper for list of people."""

    items: list[PersonListItem]
    page: int
    page_size: int
    total: int
