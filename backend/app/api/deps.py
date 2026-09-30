import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_token
from app.db.database import get_db
from app.db.models.user import User
from app.repositories.user_repository import UserRepository

# OAuth2 Bearer token extraction for Swagger / OpenAPI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """FastAPI dependency to extract, decode, and authenticate a Bearer access token.
    
    Validates:
    - Presence of Authorization header
    - JWT cryptographic signature
    - Token expiration (exp)
    - Token type (must be 'access')
    - User existence in database
    - User active status
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Enforce token type constraint: access tokens only
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: expected access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = payload.get("sub")
    if not subject:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(subject)
    except (ValueError, TypeError):
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
