import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("", response_model=SearchResponse)
def global_search(
    q: str = Query(..., min_length=2, max_length=100),
    type: Optional[str] = Query(None),
    family_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = SearchService(db)
    return service.search(
        user_id=current_user.id,
        q=q,
        type_filter=type,
        family_id=family_id,
        limit=limit
    )
