from fastapi import APIRouter, Depends, Query
from typing import List, Optional
import uuid

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.activity import ActivityResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/activity", tags=["activity"])

@router.get("", response_model=List[ActivityResponse])
def list_activity(
    family_id: Optional[uuid.UUID] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ActivityService(db)
    items, _ = svc.list_activities(current_user.id, family_id, limit, offset)
    return items
