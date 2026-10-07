with open("backend/app/db/models/__init__.py", "r") as f:
    content = f.read()

new_imports = """
from app.db.models.media import Media, MediaPerson, EventMedia
from app.db.models.album import Album, AlbumMedia
from app.db.models.memory import Memory, MemoryPerson, MemoryMedia
"""
content = content + new_imports
with open("backend/app/db/models/__init__.py", "w") as f:
    f.write(content)
