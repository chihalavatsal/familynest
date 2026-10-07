from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal, Union
import uuid
from datetime import datetime, date

class EventAudienceInput(BaseModel):
    type: Literal["family", "selected_members", "user"]
    family_id: Optional[uuid.UUID] = None
    person_ids: Optional[List[uuid.UUID]] = None
    user_id: Optional[uuid.UUID] = None

class EventParticipantInput(BaseModel):
    person_id: uuid.UUID
    status: Literal["invited", "accepted", "declined", "maybe"] = "invited"

class EventCreate(BaseModel):
    event_type: Literal["birthday", "anniversary", "family_event", "important_date", "announcement"]
    title: str
    description: Optional[str] = None
    
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    all_day: bool = False
    
    person_id: Optional[uuid.UUID] = None
    audience: EventAudienceInput
    participants: Optional[List[EventParticipantInput]] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    all_day: Optional[bool] = None
    status: Optional[Literal["active", "cancelled"]] = None
    audience: Optional[EventAudienceInput] = None
    
class EventParticipantResponse(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    person_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    title: str
    description: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    all_day: bool
    status: str
    person_id: Optional[uuid.UUID] = None
    created_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
