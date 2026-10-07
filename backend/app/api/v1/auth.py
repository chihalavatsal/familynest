import secrets
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


from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import uuid
import urllib.parse
from app.core.config import settings

@router.get("/google/login", summary="Redirect to Google OAuth consent screen")
def google_login(request: Request):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Google OAuth is not configured")
        
    # Infer the base URL dynamically if possible, or fallback to localhost
    # For a robust setup, backend URL should be in settings, but we can construct it
    backend_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{backend_url}/api/v1/auth/google/callback"
    
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)


@router.get("/google/callback", summary="Handle Google OAuth callback")
async def google_callback(request: Request, code: str = None, error: str = None, db: Session = Depends(get_db)):
    if error:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error={urllib.parse.quote(error)}")
        
    if not code:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=NoCodeProvided")
        
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=GoogleOAuthNotConfigured")

    backend_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{backend_url}/api/v1/auth/google/callback"
    
    # 1. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        if token_res.status_code != 200:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=InvalidToken")
            
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        # 2. Get user info
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if user_res.status_code != 200:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=InvalidUserInfo")
            
        user_info = user_res.json()
        email = user_info.get("email")
        if not email:
            return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=NoEmailProvided")
            
        # 3. Find or Create User
        from app.services.auth_service import AuthService
        auth_service = AuthService(db)
        
        # We need a method to login_or_register_google(email)
        user = db.query(User).filter_by(email=email).first()
        if not user:
            # Register new user
            display_name = user_info.get("name") or email.split("@")[0]
            # Create a dummy password hash since they use Google
            import bcrypt
            dummy_hash = bcrypt.hashpw(secrets.token_urlsafe(32).encode(), bcrypt.gensalt()).decode()
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=dummy_hash,
                display_name=display_name,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        # 4. Generate FamilyNest Tokens
        tokens = auth_service.create_token_pair(user)
        
        # 5. Redirect to frontend with tokens
        # A more secure way is setting HTTP-only cookies, but for this SPA pattern, passing in hash or query is common
        return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?access_token={tokens.access_token}&refresh_token={tokens.refresh_token}")



from pydantic import BaseModel
class VerifyOTPRequest(BaseModel):
    email: str
    otp_code: str

@router.post("/verify-otp", summary="Verify email OTP")
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    if user.is_verified:
        return {"message": "Already verified"}
    if user.otp_code != req.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    from datetime import datetime, timezone
    if not user.otp_expires_at or user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP has expired")
        
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    user.is_verified = True
    db.commit()
    
    # Return JWT token so they are instantly logged in
    auth_service = AuthService(db)
    return auth_service.create_token_pair(user)

from pydantic import BaseModel, constr

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp_code: str
    new_password: constr(min_length=8)

@router.post("/forgot-password", summary="Request a password reset OTP")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="No account found with this email address.")
        
    import random
    from datetime import datetime, timezone, timedelta
    import logging
    logger = logging.getLogger(__name__)
    
    otp = f"{random.randint(100000, 999999)}"
    user.otp_code = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()
    
    from app.services.email_service import email_service
    email_service.send_otp_email(to_email=user.email, otp=otp, context="password_reset")
    
    return {"message": "Verification code has been sent to your email."}

@router.post("/reset-password", summary="Reset password using OTP")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    print(f"RESET REQUEST RECEIVED: {req}")
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        print("User not found!")
        raise HTTPException(status_code=400, detail="Invalid request")
        
    if not user.otp_code or user.otp_code != req.otp_code:
        print(f"OTP Mismatch! DB OTP: {user.otp_code}, REQ OTP: {req.otp_code}")
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
    from datetime import datetime, timezone
    if not user.otp_expires_at or user.otp_expires_at < datetime.now(timezone.utc):
        print(f"OTP Expired! Exp: {user.otp_expires_at}, Now: {datetime.now(timezone.utc)}")
        raise HTTPException(status_code=400, detail="Reset code has expired")
        
    from app.services.auth_service import get_password_hash
    user.password_hash = get_password_hash(req.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    user.is_verified = True
    db.commit()
    print("RESET SUCCESSFUL!")
    
    return {"message": "Password has been reset successfully. You can now log in."}


class ResendOTPRequest(BaseModel):
    email: str

@router.post("/resend-otp", summary="Resend email verification OTP")
def resend_otp(req: ResendOTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
        
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")
        
    import random
    from datetime import datetime, timezone, timedelta
    
    otp = f"{random.randint(100000, 999999)}"
    user.otp_code = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()
    
    from app.services.email_service import email_service
    email_service.send_otp_email(to_email=user.email, otp=otp, context="verification")
    
    return {"message": "A new verification code has been sent."}
