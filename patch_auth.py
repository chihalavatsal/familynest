import re
with open('backend/app/api/v1/auth.py', 'r') as f:
    code = f.read()

new_reset = """
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
    db.commit()
    print("RESET SUCCESSFUL!")
    
    return {"message": "Password has been reset successfully. You can now log in."}
"""

code = re.sub(r'@router.post\("/reset-password".*?return {"message": "Password has been reset successfully\. You can now log in\."}', new_reset, code, flags=re.DOTALL)

with open('backend/app/api/v1/auth.py', 'w') as f:
    f.write(code)
