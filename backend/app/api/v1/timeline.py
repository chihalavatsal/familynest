from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from typing import List

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.timeline import TimelineEvent
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/people/{person_id}/timeline", tags=["people"])

@router.get("", response_model=List[TimelineEvent])
def get_person_timeline(
    person_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = TimelineService(db)
    return svc.get_timeline(person_id, current_user.id)
