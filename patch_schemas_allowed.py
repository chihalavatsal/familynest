with open("backend/app/schemas/memory.py", "r") as f:
    content = f.read()

content = content.replace(
    "    visibility: Optional[str] = 'family'",
    "    visibility: Optional[str] = 'family'\n    allowed_user_ids: Optional[list[uuid.UUID]] = None"
)
with open("backend/app/schemas/memory.py", "w") as f:
    f.write(content)

with open("backend/app/schemas/album.py", "r") as f:
    content = f.read()

content = content.replace(
    "    visibility: Optional[str] = 'family'",
    "    visibility: Optional[str] = 'family'\n    allowed_user_ids: Optional[list[uuid.UUID]] = None"
)
with open("backend/app/schemas/album.py", "w") as f:
    f.write(content)
