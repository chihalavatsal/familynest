import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EducationCreate(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class EducationUpdate(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class EducationResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
