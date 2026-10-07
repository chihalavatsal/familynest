import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.media import MediaResponse

class AlbumCreate(BaseModel):
    visibility: Optional[str] = 'family'
    allowed_user_ids: Optional[list[uuid.UUID]] = None
    family_id: uuid.UUID
    title: str
    description: Optional[str] = None

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class AlbumResponse(BaseModel):
    visibility: str
    id: uuid.UUID
    family_id: uuid.UUID
    title: str
    description: Optional[str]
    created_by_user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    media_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class AlbumDetailResponse(AlbumResponse):
    media: List[MediaResponse] = []
    
class AlbumMediaAdd(BaseModel):
    media_id: uuid.UUID
