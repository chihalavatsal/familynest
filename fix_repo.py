with open("backend/app/repositories/user_repository.py", "r") as f:
    code = f.read()

code = code.replace(
    "is_verified=is_verified,",
    "is_verified=is_verified,\n            otp_code=kwargs.get('otp_code'),\n            otp_expires_at=kwargs.get('otp_expires_at'),"
)
code = code.replace(
    "is_verified: bool = False,",
    "is_verified: bool = False,\n        **kwargs"
)

with open("backend/app/repositories/user_repository.py", "w") as f:
    f.write(code)

with open("backend/app/services/auth_service.py", "r") as f:
    scode = f.read()

scode = scode.replace("import random", "")
scode = scode.replace("from datetime import datetime, timezone, timedelta", "")
import_lines = "import random\nfrom datetime import datetime, timezone, timedelta\n"
scode = import_lines + scode

old_create = """
        user = self.user_repo.create(
            email=normalized_email,
            password_hash=hashed_password,
            display_name=req.display_name,
            is_active=True,
            is_verified=False,
        )
        
        # Generate and save OTP
        otp = f"{random.randint(100000, 999999)}"
        user.otp_code = otp
        user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        self.db.commit()
        self.db.refresh(user)
"""

new_create = """
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
"""
import re
scode = re.sub(r'        user = self\.user_repo\.create\((.*?)\s+self\.db\.refresh\(user\)', new_create, scode, flags=re.DOTALL)

with open("backend/app/services/auth_service.py", "w") as f:
    f.write(scode)

