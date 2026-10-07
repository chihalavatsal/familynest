import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.album import AlbumCreate, AlbumUpdate, AlbumResponse, AlbumDetailResponse, AlbumMediaAdd
from app.services.album_service import AlbumService

router = APIRouter()

@router.post("", response_model=AlbumResponse, status_code=status.HTTP_201_CREATED)
def create_album(
    data: AlbumCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    return service.create(data, user_id=current_user.id)

@router.get("", response_model=List[AlbumResponse])
def list_albums(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    return service.list_for_family(family_id, user_id=current_user.id)

@router.get("/{album_id}", response_model=AlbumDetailResponse)
def get_album(
    album_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    return service.get_by_id(album_id, user_id=current_user.id)

@router.patch("/{album_id}", response_model=AlbumResponse)
def update_album(
    album_id: uuid.UUID,
    data: AlbumUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    return service.update(album_id, data, user_id=current_user.id)

@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
    album_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    service.delete(album_id, user_id=current_user.id)

@router.post("/{album_id}/media", status_code=status.HTTP_200_OK)
def add_media_to_album(
    album_id: uuid.UUID,
    data: AlbumMediaAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    service.add_media(album_id, data.media_id, user_id=current_user.id)
    return {"status": "ok"}

@router.delete("/{album_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_media_from_album(
    album_id: uuid.UUID,
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AlbumService(db)
    service.remove_media(album_id, media_id, user_id=current_user.id)
