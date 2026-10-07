"""Family schemas for FamilyNest Family Network & Membership API (Phase 4).

Design rules:
- A Family is an independent network — NOT a relationship, NOT a marriage entity.
- Marriage between two People does NOT merge Family networks.
- A Person can belong to multiple Family networks simultaneously.
- claimed_by_user_id on Person is used to find the creator's claimed Person for owner membership.
- id, created_by_user_id, created_at, updated_at are NEVER client-writable.
- Phone/email from Person records are NOT exposed in membership list responses.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# Valid role values (mirrors DB CHECK constraint)
FamilyRole = Literal["owner", "admin", "member", "invited"]

# Roles that confer write/admin access to family metadata
ADMIN_ROLES = {"owner", "admin"}

# Roles that can add/remove members
MEMBER_MANAGE_ROLES = {"owner", "admin"}

# Only owner may delete the family
OWNER_ONLY_ROLES = {"owner"}

# Allowed sort fields whitelist
ALLOWED_SORT_FIELDS = {"name", "created_at", "updated_at"}
ALLOWED_SORT_DIRS = {"asc", "desc"}

# Field length limits
MAX_NAME_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 5000


# =============================================================================
# Family Schemas
# =============================================================================

class FamilyCreate(BaseModel):
    """Fields a client may supply when creating a Family.

    Excluded from client input:
    - id (server-generated UUID)
    - created_by_user_id (server-derived from auth token)
    - created_at / updated_at (server timestamps)
    """
    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Family name must not be empty or whitespace")
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"Family name must be at most {MAX_NAME_LENGTH} characters")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters")
        return v or None


class FamilyUpdate(BaseModel):
    """Fields a client may supply for a partial (PATCH) update of a Family.

    All fields are Optional. Unset fields are NOT modified.
    Use model_dump(exclude_unset=True) to get only the changed fields.
    """
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Family name must not be empty or whitespace")
        if len(v) > MAX_NAME_LENGTH:
            raise ValueError(f"Family name must be at most {MAX_NAME_LENGTH} characters")
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) > MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters")
        return v or None


class FamilyListItem(BaseModel):
    """Summary representation of a Family for paginated list responses."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class FamilyResponse(BaseModel):
    """Full detail representation of a Family."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class FamilyListResponse(BaseModel):
    """Paginated response wrapper for list of families."""
    items: list[FamilyListItem]
    page: int
    page_size: int
    total: int


# =============================================================================
# Family Membership Schemas
# =============================================================================

class FamilyMemberCreate(BaseModel):
    """Fields a client supplies when adding a Person to a Family.

    person_id must reference an existing Person.
    role defaults to 'member'.
    Client cannot assign 'owner' — that is reserved for the creator workflow.
    """
    person_id: UUID
    role: FamilyRole = "member"

    @field_validator("role")
    @classmethod
    def validate_role_not_owner(cls, v: str) -> str:
        if v == "owner":
            raise ValueError(
                "Cannot directly assign 'owner' role when adding a member. "
                "Owner is assigned automatically during family creation."
            )
        return v


class FamilyMemberUpdate(BaseModel):
    """Fields a client supplies to update a Family member's role."""
    role: FamilyRole

    @field_validator("role")
    @classmethod
    def validate_role_not_owner(cls, v: str) -> str:
        if v == "owner":
            raise ValueError(
                "Cannot directly assign 'owner' role. "
                "Owner transfer is not implemented in this phase."
            )
        return v


class FamilyMemberResponse(BaseModel):
    """Public representation of a Family member.

    Exposes safe Person fields only — no phone, email, or password data.
    """
    person_id: UUID
    family_id: UUID
    role: str
    joined_at: Optional[datetime] = None
    created_at: datetime

    # Safe Person fields
    first_name: str
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    profile_photo_url: Optional[str] = None
    profile_status: str

    model_config = ConfigDict(from_attributes=True)


class FamilyMemberListResponse(BaseModel):
    """Paginated response wrapper for family membership list."""
    items: list[FamilyMemberResponse]
    page: int
    page_size: int
    total: int
