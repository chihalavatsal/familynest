import os

with open("backend/app/api/v1/auth.py", "r") as f:
    content = f.read()

google_code = """
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

"""

# Add import secrets if not exists
if "import secrets" not in content:
    content = "import secrets\n" + content

with open("backend/app/api/v1/auth.py", "w") as f:
    f.write(content + "\n" + google_code)

print("Added Google OAuth routes to backend")
