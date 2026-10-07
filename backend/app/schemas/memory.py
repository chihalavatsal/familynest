import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.media import MediaResponse
from app.schemas.person import PersonListItem

class MemoryCreate(BaseModel):
    visibility: Optional[str] = 'family'
    allowed_user_ids: Optional[list[uuid.UUID]] = None
    family_id: uuid.UUID
    title: str
    body: str
    memory_date: Optional[date] = None

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    memory_date: Optional[date] = None

class MemoryResponse(BaseModel):
    visibility: str
    id: uuid.UUID
    family_id: uuid.UUID
    title: str
    body: str
    memory_date: Optional[date]
    created_by_user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    tagged_people: List[PersonListItem] = []
    media: List[MediaResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
    
class MemoryPersonAdd(BaseModel):
    person_id: uuid.UUID

class MemoryMediaAdd(BaseModel):
    media_id: uuid.UUID
