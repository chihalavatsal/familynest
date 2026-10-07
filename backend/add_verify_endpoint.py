import os

with open("backend/app/api/v1/auth.py", "r") as f:
    content = f.read()

verify_code = """
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
    db.commit()
    
    # Return JWT token so they are instantly logged in
    auth_service = AuthService(db)
    return auth_service.create_token_pair(user)
"""

with open("backend/app/api/v1/auth.py", "a") as f:
    f.write("\n" + verify_code)

print("Added verify-otp endpoint")
