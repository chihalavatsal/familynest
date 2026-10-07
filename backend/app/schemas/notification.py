import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AudienceType(str, Enum):
    FAMILY = "family"
    SELECTED_MEMBERS = "selected_members"
    USER = "user"


class NotificationAudienceInput(BaseModel):
    type: AudienceType
    family_id: Optional[uuid.UUID] = None
    person_ids: Optional[List[uuid.UUID]] = None
    user_id: Optional[uuid.UUID] = None


class NotificationCreate(BaseModel):
    notification_type: str = Field(..., max_length=50)
    title: str = Field(..., max_length=100)
    body: str
    audience: NotificationAudienceInput


class NotificationResponse(BaseModel):
    id: uuid.UUID
    notification_type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime
    target_type: Optional[str] = None
    target_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int


class NotificationPreferenceResponse(BaseModel):
    in_app_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class NotificationPreferenceUpdate(BaseModel):
    in_app_enabled: bool
