import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.schemas.memory import MemoryCreate, MemoryUpdate, MemoryResponse, MemoryPersonAdd, MemoryMediaAdd
from app.services.memory_service import MemoryService

router = APIRouter()

@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    return service.create(data, user_id=current_user.id)

@router.get("", response_model=List[MemoryResponse])
def list_memories(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    return service.list_for_family(family_id, user_id=current_user.id)

@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    return service.get_by_id(memory_id, user_id=current_user.id)

@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    memory_id: uuid.UUID,
    data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    return service.update(memory_id, data, user_id=current_user.id)

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    memory_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    service.delete(memory_id, user_id=current_user.id)

@router.post("/{memory_id}/people", status_code=status.HTTP_200_OK)
def add_person_to_memory(
    memory_id: uuid.UUID,
    data: MemoryPersonAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    service.add_person(memory_id, data.person_id, user_id=current_user.id)
    return {"status": "ok"}

@router.delete("/{memory_id}/people/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_person_from_memory(
    memory_id: uuid.UUID,
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    service.remove_person(memory_id, person_id, user_id=current_user.id)

@router.post("/{memory_id}/media", status_code=status.HTTP_200_OK)
def add_media_to_memory(
    memory_id: uuid.UUID,
    data: MemoryMediaAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    service.add_media(memory_id, data.media_id, user_id=current_user.id)
    return {"status": "ok"}

@router.delete("/{memory_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_media_from_memory(
    memory_id: uuid.UUID,
    media_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = MemoryService(db)
    service.remove_media(memory_id, media_id, user_id=current_user.id)
