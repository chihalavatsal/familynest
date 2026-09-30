from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditLogResponse(AuditLogBase):
    id: UUID
    actor_user_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
