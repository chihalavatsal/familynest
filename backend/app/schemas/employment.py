import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class EmploymentCreate(BaseModel):
    employer_name: str
    job_title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = True

class EmploymentUpdate(BaseModel):
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None

class EmploymentResponse(BaseModel):
    id: uuid.UUID
    person_id: uuid.UUID
    employer_name: str
    job_title: str
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
