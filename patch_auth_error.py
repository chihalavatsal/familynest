import os

with open('backend/app/services/email_service.py', 'r') as f:
    code = f.read()

old_code = """
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
"""

new_code = """
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            self.last_error = str(e)
            return False
"""

if "self.last_error = str(e)" not in code:
    code = code.replace(old_code, new_code)
    with open('backend/app/services/email_service.py', 'w') as f:
        f.write(code)

with open('backend/app/api/v1/auth.py', 'r') as f:
    code2 = f.read()

old_code2 = """
    if not success:
        import traceback
        return {"message": "Verification code has been sent to your email.", "debug_email_status": "FAILED", "is_configured": getattr(email_service, 'is_configured', False)}
"""

new_code2 = """
    if not success:
        import traceback
        return {"message": "Verification code has been sent to your email.", "debug_email_status": "FAILED", "is_configured": getattr(email_service, 'is_configured', False), "error": getattr(email_service, 'last_error', 'unknown')}
"""

if "getattr(email_service, 'last_error'" not in code2:
    code2 = code2.replace(old_code2, new_code2)
    with open('backend/app/api/v1/auth.py', 'w') as f:
        f.write(code2)
