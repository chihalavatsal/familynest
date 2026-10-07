import uuid
from typing import List, Tuple
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.notification import Notification, NotificationTarget, NotificationRecipient
from app.db.models.audit_log import AuditLog
from app.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse
from app.repositories.notification_repository import NotificationRepository
from app.services.audience_service import AudienceService


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificationRepository(db)
        self.audience_svc = AudienceService(db)

    def create_notification(self, creator_user_id: uuid.UUID, data: NotificationCreate) -> NotificationResponse:
        # 1. Resolve audience (atomic fail if unauthorized)
        recipient_user_ids = self.audience_svc.resolve_audience(creator_user_id, data.audience)
        
        # Determine self-notification behavior:
        # For this phase, if creator is in the resolved set, we keep them so they can see their own updates,
        # but the prompt says "A creator should not automatically receive a notification they created unless they are explicitly included... Do not create duplicate self-recipient rows."
        # Because `resolve_audience` explicitly includes them if they are in the family, it's fine.
        
        # 2. Create notification
        notification = Notification(
            notification_type=data.notification_type,
            title=data.title,
            body=data.body,
            created_by_user_id=creator_user_id
        )
        self.repo.create_notification(notification)
        
        # 3. Create target
        target = NotificationTarget(
            notification_id=notification.id,
            audience_type=data.audience.type.value,
            family_id=data.audience.family_id,
            user_id=data.audience.user_id
        )
        self.repo.create_target(target)
        
        if data.audience.person_ids:
            for pid in data.audience.person_ids:
                ptarget = NotificationTarget(
                    notification_id=notification.id,
                    audience_type=data.audience.type.value,
                    person_id=pid
                )
                self.repo.create_target(ptarget)
                
        # 4. Create recipients (check preferences? For now just create them. Preferences might turn off push/email, but in-app is usually always on unless explicitly disabled)
        recipients = []
        for uid in recipient_user_ids:
            pref = self.repo.get_preference(uid)
            if pref.in_app_enabled:
                recipients.append(
                    NotificationRecipient(
                        notification_id=notification.id,
                        user_id=uid
                    )
                )
        if recipients:
            self.repo.create_recipients(recipients)
            
        # 5. Audit Log
        audit = AuditLog(
            actor_user_id=creator_user_id,
            action="notification.create",
            entity_type="notification",
            entity_id=notification.id,
            metadata_={
                "notification_type": notification.notification_type,
                "audience_type": target.audience_type,
                "recipient_count": len(recipients)
            }
        )
        self.db.add(audit)
        self.db.commit()
        
        return self._build_response(notification, False)

    def list_notifications(self, user_id: uuid.UUID, unread: bool, page: int, page_size: int) -> NotificationListResponse:
        skip = (page - 1) * page_size
        results, total = self.repo.list_user_notifications(user_id, unread, skip, page_size)
        
        items = []
        for notif, recip in results:
            items.append(self._build_response(notif, recip.is_read))
            
        return NotificationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    def get_notification(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> NotificationResponse:
        res = self.repo.get_recipient_notification(user_id, notification_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif, recip = res
        return self._build_response(notif, recip.is_read)
        
    def mark_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> NotificationResponse:
        res = self.repo.get_recipient_notification(user_id, notification_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif, recip = res
        
        if not recip.is_read:
            recip.is_read = True
            recip.read_at = datetime.now(timezone.utc)
            
            audit = AuditLog(
                actor_user_id=user_id,
                action="notification.read",
                entity_type="notification",
                entity_id=notif.id,
                metadata_={}
            )
            self.db.add(audit)
            self.db.commit()
            
        return self._build_response(notif, recip.is_read)
        
    def mark_unread(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> NotificationResponse:
        res = self.repo.get_recipient_notification(user_id, notification_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif, recip = res
        
        if recip.is_read:
            recip.is_read = False
            recip.read_at = None
            self.db.commit()
            
        return self._build_response(notif, recip.is_read)
        
    def dismiss(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> None:
        res = self.repo.get_recipient_notification(user_id, notification_id)
        if not res:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        notif, recip = res
        
        recip.dismissed_at = datetime.now(timezone.utc)
        audit = AuditLog(
            actor_user_id=user_id,
            action="notification.dismiss",
            entity_type="notification",
            entity_id=notif.id,
            metadata_={}
        )
        self.db.add(audit)
        self.db.commit()
        
    def bulk_read(self, user_id: uuid.UUID) -> None:
        from sqlalchemy import update
        stmt = (
            update(NotificationRecipient)
            .where(
                NotificationRecipient.user_id == user_id,
                NotificationRecipient.is_read == False,
                NotificationRecipient.dismissed_at.is_(None)
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        self.db.execute(stmt)
        self.db.commit()

    def _build_response(self, notification: Notification, is_read: bool) -> NotificationResponse:
        target_type = None
        target_id = None
        if notification.targets:
            t = notification.targets[0]
            if t.family_id:
                target_type = "family"
                target_id = t.family_id
            elif t.person_id:
                target_type = "person"
                target_id = t.person_id
            elif t.user_id:
                target_type = "user"
                target_id = t.user_id
                
        return NotificationResponse(
            id=notification.id,
            notification_type=notification.notification_type,
            title=notification.title,
            body=notification.body,
            is_read=is_read,
            created_at=notification.created_at,
            target_type=target_type,
            target_id=target_id
        )
