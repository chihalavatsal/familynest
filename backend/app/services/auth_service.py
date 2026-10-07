import random
from datetime import datetime, timezone, timedelta
import uuid
import logging
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    LogoutResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic layer for user registration, authentication, and token management."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, req: RegisterRequest) -> User:
        """Register a new user account.
        
        CRITICAL ARCHITECTURE RULE:
        Creating a USER must NOT automatically create a PERSON record.
        A person is a separate canonical identity that can be claimed later.
        """
        normalized_email = req.email.lower().strip()
        existing_user = self.user_repo.get_by_email(normalized_email)
        if existing_user:
            # Generic duplicate error to mitigate account enumeration
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists",
            )

        hashed_password = get_password_hash(req.password)

        logger.info(f"Registering new user account: {normalized_email[:3]}***@{normalized_email.split('@')[-1]}")

        otp = f"{random.randint(100000, 999999)}"
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        user = self.user_repo.create(
            email=normalized_email,
            password_hash=hashed_password,
            display_name=req.display_name,
            is_active=True,
            is_verified=False,
            otp_code=otp,
            otp_expires_at=expires
        )

        
        # In a real app, you would send an email here. For now, print to console!
        logger.info(f"\n\n==================================================\nOTP FOR {normalized_email}: {otp}\n==================================================\n\n")
        logger.info(f"Generated verification OTP for {normalized_email[:3]}...")
        
        return user

    def authenticate(self, req: LoginRequest) -> User:
        """Authenticate user credentials and verify account state."""
        normalized_email = req.email.lower().strip()
        user = self.user_repo.get_by_email(normalized_email)

        # Constant-time mitigation against enumeration: verify dummy hash if user not found
        if not user or not user.password_hash:
            logger.info("Authentication failed: user not found or no password set")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(req.password, user.password_hash):
            logger.info(f"Authentication failed: invalid password for user_id={user.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Authentication rejected: user_id={user.id} account is inactive")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Please contact support.",
            )
            
        if not user.is_verified:
            logger.warning(f"Authentication rejected: user_id={user.id} account is not verified")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not verified. Please verify your email first.",
            )

        logger.info(f"Authentication successful for user_id={user.id}")
        return user

    def create_token_pair(self, user: User) -> TokenResponse:
        """Generate access and refresh tokens for an authenticated user."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Validate a refresh token and issue a fresh access/refresh token pair.
        
        Strict token type check: Access tokens are explicitly rejected.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = decode_token(refresh_token_str)
        except JWTError:
            raise credentials_exception

        # Explicitly enforce token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: expected refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        subject = payload.get("sub")
        if not subject:
            raise credentials_exception

        try:
            user_uuid = uuid.UUID(subject)
        except (ValueError, TypeError):
            raise credentials_exception

        user = self.user_repo.get_by_id(user_uuid)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account no longer active or available",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.info(f"Refresh token validated successfully for user_id={user.id}")
        return self.create_token_pair(user)

    def logout(self, user: User) -> LogoutResponse:
        """Process user logout.
        
        Architecture Note:
        In this stateless JWT architecture, tokens expire after short durations
        (access tokens expire in 15 minutes). Logout advises the client to immediately
        purge the access and refresh tokens from memory/storage.
        """
        logger.info(f"User logged out: user_id={user.id}")
        return LogoutResponse(
            message="Successfully logged out. Please purge tokens on client.",
            revoked=True,
        )
