import re

with open('backend/app/services/profile_service.py', 'r') as f:
    content = f.read()

# Fix update_person_profile
content = re.sub(
    r'self\.db\.flush\(\)\n\s+return person',
    r'self.db.commit()\n        self.db.refresh(person)\n        return person',
    content
)

# Fix update_privacy_settings
content = re.sub(
    r'self\.db\.flush\(\)\n\s+return settings',
    r'self.db.commit()\n        self.db.refresh(settings)\n        return settings',
    content
)

with open('backend/app/services/profile_service.py', 'w') as f:
    f.write(content)
