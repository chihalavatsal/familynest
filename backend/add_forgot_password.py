with open("backend/app/api/v1/auth.py", "r") as f:
    code = f.read()

new_endpoints = """
from pydantic import BaseModel, constr

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp_code: str
    new_password: constr(min_length=8)

@router.post("/forgot-password", summary="Request password reset OTP")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if user:
        import random
        from datetime import datetime, timezone, timedelta
        import logging
        logger = logging.getLogger(__name__)
        
        otp = f"{random.randint(100000, 999999)}"
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.commit()
        
        logger.info(f"\\n\\n{'='*50}\\nPASSWORD RESET OTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")
        print(f"\\n\\n{'='*50}\\nPASSWORD RESET OTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")
        
    return {"message": "If an account with that email exists, we have sent a password reset code."}

@router.post("/reset-password", summary="Reset password using OTP")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
        
    if not user.otp_code or user.otp_code != req.otp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        
    from datetime import datetime, timezone
    if not user.otp_expires_at or user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset code has expired")
        
    from app.services.auth_service import get_password_hash
    user.password_hash = get_password_hash(req.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    return {"message": "Password has been reset successfully. You can now log in."}
"""

with open("backend/app/api/v1/auth.py", "a") as f:
    f.write(new_endpoints)

