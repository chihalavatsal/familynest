from typing import Optional, List
from pydantic import BaseModel, ConfigDict
import uuid

class SearchResult(BaseModel):
    id: uuid.UUID
    type: str # 'person', 'family', 'memory', 'album', 'event'
    title: str
    subtitle: Optional[str] = None
    family_id: Optional[uuid.UUID] = None
    family_name: Optional[str] = None
    route: str
    
    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    items: List[SearchResult]
    total: int
