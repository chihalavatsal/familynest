from typing import List, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "FamilyNest"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security / JWT Authentication
    JWT_SECRET_KEY: str # Required. No insecure fallback.
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Backward compatibility aliases
    SECRET_KEY: Optional[str] = None
    ALGORITHM: Optional[str] = None

    @model_validator(mode="after")
    def sync_jwt_secret(self) -> "Settings":
        if self.SECRET_KEY and self.JWT_SECRET_KEY == "familynest_dev_jwt_secret_key_change_in_production_32chars":
            self.JWT_SECRET_KEY = self.SECRET_KEY
        if self.ALGORITHM and self.JWT_ALGORITHM == "HS256":
            self.JWT_ALGORITHM = self.ALGORITHM
        return self

    # Neon PostgreSQL Database Connection URL
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def clean_database_url(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip("'\" \t\r\n")
        return v

    # SMTP / Email Configuration (Brevo)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: str = "noreply@familynest.app"
    EMAILS_FROM_NAME: str = "FamilyNest"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://familynest-kappa.vercel.app",
        "https://familynest.vercel.app",
    ]

    # Google OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=os.path.join(Path(__file__).resolve().parent.parent.parent.parent, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
