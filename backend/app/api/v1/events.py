from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
import uuid

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventParticipantResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    return svc.create_event(current_user.id, event_in)

@router.get("", response_model=List[EventResponse])
def list_events(
    event_type: Optional[str] = None,
    upcoming: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    events, _ = svc.list_events(current_user.id, limit, offset, event_type, upcoming)
    return events
    
@router.get("/upcoming", response_model=List[EventResponse])
def list_upcoming_events(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    events, _ = svc.list_events(current_user.id, limit, offset, upcoming=True)
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    return svc.get_event(event_id, current_user.id)

@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: uuid.UUID,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    return svc.update_event(event_id, current_user.id, event_in)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    svc.delete_event(event_id, current_user.id)

@router.post("/{event_id}/participants", response_model=EventParticipantResponse, status_code=status.HTTP_201_CREATED)
def add_participant(
    event_id: uuid.UUID,
    person_id: uuid.UUID = Query(...),
    participant_status: str = Query("invited"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    return svc.add_participant(event_id, current_user.id, person_id, participant_status)

@router.get("/{event_id}/participants", response_model=List[EventParticipantResponse])
def list_participants(
    event_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    items, _ = svc.list_participants(event_id, current_user.id, limit, offset)
    return items

@router.delete("/{event_id}/participants/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participant(
    event_id: uuid.UUID,
    person_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = EventService(db)
    svc.delete_participant(event_id, person_id, current_user.id)
