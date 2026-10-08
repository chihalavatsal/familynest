import re

with open('backend/app/services/person_claim_service.py', 'r') as f:
    code = f.read()

old_code = """        person.claimed_by_user_id = user_id
        invitation.status = "accepted"

        # Cancel others"""
new_code = """        person.claimed_by_user_id = user_id
        person.profile_status = "claimed"
        invitation.status = "accepted"

        # Cancel others"""

code = code.replace(old_code, new_code)
with open('backend/app/services/person_claim_service.py', 'w') as f:
    f.write(code)
