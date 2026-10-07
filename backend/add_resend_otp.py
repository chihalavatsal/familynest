import re

with open("backend/app/api/v1/auth.py", "r") as f:
    code = f.read()

resend_endpoint = """
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
    import logging
    logger = logging.getLogger(__name__)
    
    otp = f"{random.randint(100000, 999999)}"
    user.otp_code = otp
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    db.commit()
    
    logger.info(f"\\n\\n{'='*50}\\nOTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")
    print(f"\\n\\n{'='*50}\\nOTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")
    
    return {"message": "A new verification code has been sent."}
"""

with open("backend/app/api/v1/auth.py", "a") as f:
    f.write(resend_endpoint)

