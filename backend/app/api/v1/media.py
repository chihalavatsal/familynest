import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.media import MediaCreate, MediaResponse
from app.services.media_service import MediaService

router = APIRouter()

@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
def create_media(
    data: MediaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MediaService(db)
    return service.create(data, user_id=current_user.id)

@router.get("", response_model=List[MediaResponse])
def list_media(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MediaService(db)
    return service.list_for_family(family_id, user_id=current_user.id)

@router.get("/{media_id}", response_model=MediaResponse)
def get_media(
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MediaService(db)
    return service.get_by_id(media_id, user_id=current_user.id)

@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MediaService(db)
    service.delete(media_id, user_id=current_user.id)
