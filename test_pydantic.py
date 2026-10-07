from datetime import date
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
import uuid

class TimelineEvent(BaseModel):
    id: UUID
    date: Optional[date] = None
    year: Optional[int] = None
    title: str
    description: Optional[str] = None
    icon: str

try:
    event = TimelineEvent(
        id=uuid.uuid4(),
        date=date(2026, 10, 6),
        year=2026,
        title="Test",
        description="Test desc",
        icon="birth"
    )
    print("Success:", event)
except Exception as e:
    print("Error:", repr(e))
