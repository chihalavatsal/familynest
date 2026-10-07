with open("backend/app/schemas/memory.py", "r") as f:
    content = f.read()

content = content.replace(
    "class MemoryCreate(BaseModel):",
    "class MemoryCreate(BaseModel):\n    visibility: Optional[str] = 'family'"
)
content = content.replace(
    "class MemoryResponse(BaseModel):",
    "class MemoryResponse(BaseModel):\n    visibility: str"
)
with open("backend/app/schemas/memory.py", "w") as f:
    f.write(content)

with open("backend/app/schemas/album.py", "r") as f:
    content = f.read()

content = content.replace(
    "class AlbumCreate(BaseModel):",
    "class AlbumCreate(BaseModel):\n    visibility: Optional[str] = 'family'"
)
content = content.replace(
    "class AlbumResponse(BaseModel):",
    "class AlbumResponse(BaseModel):\n    visibility: str"
)
with open("backend/app/schemas/album.py", "w") as f:
    f.write(content)
