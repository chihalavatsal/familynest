with open("backend/app/services/privacy_service.py", "r") as f:
    c = f.read()
c = c.replace("from app.db.models.privacy import PersonPrivacySettings", "from app.db.models.privacy import PersonPrivacySettings, FamilyPrivacySettings")
c = c.replace("from app.db.models.privacy import FamilyPrivacySettings\n        ", "")
with open("backend/app/services/privacy_service.py", "w") as f:
    f.write(c)
