from pydantic import BaseModel, ConfigDict
import uuid
from typing import Optional

class PersonPrivacySettingsResponse(BaseModel):
    person_id: uuid.UUID
    phone_visibility: str
    email_visibility: str
    dob_visibility: str
    bio_visibility: str
    model_config = ConfigDict(from_attributes=True)

class PersonPrivacySettingsUpdate(BaseModel):
    phone_visibility: Optional[str] = None
    email_visibility: Optional[str] = None
    dob_visibility: Optional[str] = None
    bio_visibility: Optional[str] = None

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
