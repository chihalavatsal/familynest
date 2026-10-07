from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class ActivityResponse(BaseModel):
    id: uuid.UUID
    activity_type: str
    entity_type: str
    entity_id: uuid.UUID
    actor_user_id: Optional[uuid.UUID] = None
    family_id: Optional[uuid.UUID] = None
    metadata: Dict[str, Any] = Field(validation_alias='metadata_', default_factory=dict)
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
