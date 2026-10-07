with open("backend/app/db/models/__init__.py", "r") as f:
    c = f.read()

c = c.replace("from app.db.models.privacy import PersonPrivacySettings", "from app.db.models.privacy import PersonPrivacySettings, FamilyPrivacySettings")
c = c.replace("from app.db.models.memory import Memory, MemoryPerson, MemoryMedia", "from app.db.models.memory import Memory, MemoryPerson, MemoryMedia, MemoryAllowedUser")
c = c.replace("from app.db.models.album import Album, AlbumMedia", "from app.db.models.album import Album, AlbumMedia, AlbumAllowedUser")

with open("backend/app/db/models/__init__.py", "w") as f:
    f.write(c)
