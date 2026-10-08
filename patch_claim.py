import os
import re

with open('backend/app/services/person_claim_service.py', 'r') as f:
    code = f.read()

# Fix missing person.profile_status = "claimed"
old_code = """        try:
            # Update person
            person.claimed_by_user_id = user_id"""
new_code = """        try:
            # Update person
            person.claimed_by_user_id = user_id
            person.profile_status = "claimed" """

if 'person.profile_status = "claimed"' not in code.split('accept_invitation_by_id')[1]:
    code = code.replace(old_code, new_code)
    with open('backend/app/services/person_claim_service.py', 'w') as f:
        f.write(code)
