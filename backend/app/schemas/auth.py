import re
from typing import Optional
from pydantic import BaseModel, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class RegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: str
    password: str
    display_name: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_and_validate_email(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Email must be a string")
        v = v.strip().lower()
        if not v:
            raise ValueError("Email cannot be empty")
        if not EMAIL_REGEX.match(v) or ".." in v or v.endswith("."):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password cannot be empty or whitespace-only")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if len(v) > 128:
            raise ValueError("Password cannot exceed 128 characters")
        return v


class LoginRequest(BaseModel):
    """Schema for user login request."""
    email: str
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_and_validate_email(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Email must be a string")
        v = v.strip().lower()
        if not v:
            raise ValueError("Email cannot be empty")
        if not EMAIL_REGEX.match(v) or ".." in v or v.endswith("."):
            raise ValueError("Invalid email address format")
        return v

    @field_validator("password")
    @classmethod
    def check_password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password cannot be empty")
        return v


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str

    @field_validator("refresh_token")
    @classmethod
    def check_token_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Refresh token cannot be empty")
        return v.strip()


class TokenResponse(BaseModel):
    """Authentication tokens returned upon successful login or refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds


class LogoutResponse(BaseModel):
    """Logout confirmation response."""
    message: str
    revoked: bool
