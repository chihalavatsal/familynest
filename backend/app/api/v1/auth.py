from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.user import User
from app.api.deps import get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    LogoutResponse,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Registers an email/password account. NOTE: A User is not a Person; no Person record is created.",
)
def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    auth_service = AuthService(db)
    user = auth_service.register(req)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login with email and password",
    description="Authenticates credentials and returns a short-lived access token and a refresh token.",
)
def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate credentials and return JWT token pair."""
    auth_service = AuthService(db)
    user = auth_service.authenticate(req)
    return auth_service.create_token_pair(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchanges a valid refresh token for a new token pair. Access tokens are rejected here.",
)
def refresh_token(
    req: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Issue a new access token using a valid refresh token."""
    auth_service = AuthService(db)
    return auth_service.refresh(req.refresh_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logs out the current session. In this stateless JWT model, the client purges stored tokens.",
)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout current user."""
    auth_service = AuthService(db)
    return auth_service.logout(current_user)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the safe profile of the currently authenticated user. Requires Bearer access token.",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    """Return profile of authenticated user."""
    return current_user
