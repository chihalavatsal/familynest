with open("backend/app/api/v1/auth.py", "r") as f:
    code = f.read()

code = code.replace("user.otp_expires_at = None", "user.otp_expires_at = None\n    user.is_verified = True")

with open("backend/app/api/v1/auth.py", "w") as f:
    f.write(code)
