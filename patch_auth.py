import os

with open('backend/app/api/v1/auth.py', 'r') as f:
    code = f.read()

# Replace the email sending part in forgot_password
old_code = """
    from app.services.email_service import email_service
    email_service.send_otp_email(to_email=user.email, otp=otp, context="password_reset")
    
    return {"message": "Verification code has been sent to your email."}
"""

new_code = """
    from app.services.email_service import email_service
    success = email_service.send_otp_email(to_email=user.email, otp=otp, context="password_reset")
    
    if not success:
        import traceback
        return {"message": "Verification code has been sent to your email.", "debug_email_status": "FAILED", "is_configured": getattr(email_service, 'is_configured', False)}
    
    return {"message": "Verification code has been sent to your email.", "debug_email_status": "SUCCESS"}
"""

if "debug_email_status" not in code:
    code = code.replace(old_code, new_code)
    with open('backend/app/api/v1/auth.py', 'w') as f:
        f.write(code)
