import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from app.db.models.notification import Notification, NotificationTarget, NotificationRecipient, NotificationPreference

class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def create_target(self, target: NotificationTarget) -> NotificationTarget:
        self.db.add(target)
        self.db.flush()
        return target

    def create_recipients(self, recipients: List[NotificationRecipient]) -> None:
        self.db.add_all(recipients)
        self.db.flush()

    def get_recipient_notification(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> Optional[Tuple[Notification, NotificationRecipient]]:
        stmt = (
            select(Notification, NotificationRecipient)
            .join(NotificationRecipient, Notification.id == NotificationRecipient.notification_id)
            .where(
                NotificationRecipient.user_id == user_id,
                Notification.id == notification_id,
                NotificationRecipient.dismissed_at.is_(None)
            )
        )
        return self.db.execute(stmt).first()

    def list_user_notifications(self, user_id: uuid.UUID, unread_only: bool, skip: int, limit: int) -> Tuple[List[Tuple[Notification, NotificationRecipient]], int]:
        base_stmt = (
            select(Notification, NotificationRecipient)
            .join(NotificationRecipient, Notification.id == NotificationRecipient.notification_id)
            .where(
                NotificationRecipient.user_id == user_id,
                NotificationRecipient.dismissed_at.is_(None)
            )
        )
        if unread_only:
            base_stmt = base_stmt.where(NotificationRecipient.is_read == False)
            
        count_stmt = select(func.count(NotificationRecipient.id)).where(
            NotificationRecipient.user_id == user_id,
            NotificationRecipient.dismissed_at.is_(None)
        )
        if unread_only:
            count_stmt = count_stmt.where(NotificationRecipient.is_read == False)
        
        total = self.db.execute(count_stmt).scalar_one()

        stmt = base_stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        results = self.db.execute(stmt).all()
        return results, total

    def get_preference(self, user_id: uuid.UUID) -> NotificationPreference:
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        pref = self.db.execute(stmt).scalar_one_or_none()
        if not pref:
            pref = NotificationPreference(user_id=user_id, in_app_enabled=True)
            self.db.add(pref)
            self.db.flush()
        return pref
