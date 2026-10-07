import re
with open("backend/app/api/v1/auth.py", "r") as f:
    code = f.read()

bad_string = """    print(f"

{'='*50}
PASSWORD RESET OTP FOR {user.email}: {otp}
{'='*50}

")"""

good_string = """    print(f"\\n\\n{'='*50}\\nPASSWORD RESET OTP FOR {user.email}: {otp}\\n{'='*50}\\n\\n")"""

code = code.replace(bad_string, good_string)

with open("backend/app/api/v1/auth.py", "w") as f:
    f.write(code)
