import re
with open("backend/app/services/auth_service.py", "r") as f:
    code = f.read()

# Change the error detail for invalid password
code = re.sub(
    r'if not verify_password\(req\.password, user\.password_hash\):\s*logger\.info\(f"Authentication failed: invalid password for user_id={user\.id}"\)\s*raise HTTPException\(\s*status_code=status\.HTTP_401_UNAUTHORIZED,\s*detail="Incorrect email or password",',
    r'if not verify_password(req.password, user.password_hash):\n            logger.info(f"Authentication failed: invalid password for user_id={user.id}")\n            raise HTTPException(\n                status_code=status.HTTP_401_UNAUTHORIZED,\n                detail="Incorrect password",',
    code
)

with open("backend/app/services/auth_service.py", "w") as f:
    f.write(code)
