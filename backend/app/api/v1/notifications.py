import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate
)
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification targeting a specific audience."""
    svc = NotificationService(db)
    return svc.create_notification(current_user.id, data)


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread: bool = Query(False, description="Filter for unread notifications only"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List notifications for the current user."""
    svc = NotificationService(db)
    return svc.list_notifications(current_user.id, unread, page, page_size)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def bulk_read_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications as read."""
    svc = NotificationService(db)
    svc.bulk_read(current_user.id)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific notification."""
    svc = NotificationService(db)
    return svc.get_notification(current_user.id, notification_id)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    svc = NotificationService(db)
    return svc.mark_read(current_user.id, notification_id)


@router.post("/{notification_id}/unread", response_model=NotificationResponse)
def mark_notification_unread(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as unread."""
    svc = NotificationService(db)
    return svc.mark_unread(current_user.id, notification_id)


@router.post("/{notification_id}/dismiss", status_code=status.HTTP_204_NO_CONTENT)
def dismiss_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dismiss a notification."""
    svc = NotificationService(db)
    svc.dismiss(current_user.id, notification_id)


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences."""
    repo = NotificationRepository(db)
    pref = repo.get_preference(current_user.id)
    return pref


@router.patch("/preferences", response_model=NotificationPreferenceResponse)
def update_preferences(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences."""
    repo = NotificationRepository(db)
    pref = repo.get_preference(current_user.id)
    pref.in_app_enabled = data.in_app_enabled
    db.commit()
    db.refresh(pref)
    return pref
