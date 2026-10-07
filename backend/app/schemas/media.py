import uuid
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.person import PersonListItem

class MediaCreate(BaseModel):
    family_id: uuid.UUID
    original_filename: str
    mime_type: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class MediaResponse(BaseModel):
    id: uuid.UUID
    family_id: uuid.UUID
    uploaded_by_user_id: Optional[uuid.UUID]
    
    # We omit storage_provider and storage_object_key to avoid leaking internals
    # Instead, we will eventually provide an access_url, but for now it's null
    access_url: Optional[str] = None
    
    original_filename: str
    mime_type: str
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    status: str
    
    created_at: datetime
    updated_at: datetime
    
    tagged_people: List[PersonListItem] = []
    
    model_config = ConfigDict(from_attributes=True)
