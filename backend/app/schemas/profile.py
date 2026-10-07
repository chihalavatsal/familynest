from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Literal, Dict, Any
import uuid
from datetime import datetime, date
from app.schemas.event import EventResponse
from app.schemas.activity import ActivityResponse

class CurrentUserProfile(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PersonListItem(BaseModel):
    id: uuid.UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    is_deceased: bool
    is_minor: bool
    profile_status: str
    
    # Sensitive fields rendered optionally depending on privacy resolver
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PrivacySettingsResponse(BaseModel):
    phone_visibility: str
    email_visibility: str
    dob_visibility: str
    bio_visibility: str
    
    model_config = ConfigDict(from_attributes=True)
    
class PrivacySettingsUpdate(BaseModel):
    phone_visibility: Optional[Literal["private", "family", "public"]] = None
    email_visibility: Optional[Literal["private", "family", "public"]] = None
    dob_visibility: Optional[Literal["private", "family", "public"]] = None
    bio_visibility: Optional[Literal["private", "family", "public"]] = None

class ProfileCompletenessResponse(BaseModel):
    percentage: int
    completed: List[str]
    missing: List[str]
    
class FamilySummary(BaseModel):
    id: uuid.UUID
    name: str
    role: str
    member_count: int

class NotificationSummary(BaseModel):
    unread_count: int
    recent: List[Dict[str, Any]] = []

class RelationshipSummary(BaseModel):
    parents_count: int
    children_count: int
    siblings_count: int
    spouses_count: int
    
class DashboardResponse(BaseModel):
    profile: Optional[PersonListItem] = None
    families: List[FamilySummary] = []
    upcoming_events: List[EventResponse] = []
    notifications: NotificationSummary
    recent_activity: List[ActivityResponse] = []
    relationship_summary: RelationshipSummary

class FamilyOverviewResponse(BaseModel):
    id: uuid.UUID
    name: str
    member_count: int
    upcoming_events: List[EventResponse] = []
    recent_activity: List[ActivityResponse] = []

class PersonProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    birth_place: Optional[str] = None
    current_city: Optional[str] = None
    occupation: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    profile_photo_url: Optional[str] = None


class FamilyPrivacySettingsResponse(BaseModel):
    family_id: uuid.UUID
    allow_member_discovery: bool
    default_content_visibility: str
    member_invites_role: str
    member_management_role: str
    model_config = ConfigDict(from_attributes=True)

class FamilyPrivacySettingsUpdate(BaseModel):
    allow_member_discovery: Optional[bool] = None
    default_content_visibility: Optional[str] = None
    member_invites_role: Optional[str] = None
    member_management_role: Optional[str] = None
