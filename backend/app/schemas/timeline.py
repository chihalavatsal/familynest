from pydantic import BaseModel
from typing import Optional
from datetime import date as dt_date
from uuid import UUID

class TimelineEvent(BaseModel):
    id: UUID
    date: Optional[dt_date] = None
    year: Optional[int] = None
    title: str
    description: Optional[str] = None
    icon: str  # birth, death, marriage, job, education, child
