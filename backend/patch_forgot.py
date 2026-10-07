with open("backend/app/api/v1/auth.py", "r") as f:
    code = f.read()

import re

# We will just replace everything between @router.post("/forgot-password" and @router.post("/reset-password"
pattern = r'@router\.post\("/forgot-password".*?(?=@router\.post\("/reset-password")'

new_forgot = """@router.post("/forgot-password", summary="Request a password reset OTP")
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
    
    logger.info(f"PASSWORD RESET OTP FOR {user.email}: {otp}")
    print(f"\\n\\n{'='*50}\\nPASSWORD RESET OTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")
    
    return {"message": "Verification code has been sent to your email."}

"""

code = re.sub(pattern, new_forgot, code, flags=re.DOTALL)

with open("backend/app/api/v1/auth.py", "w") as f:
    f.write(code)
