import asyncio
import logging
from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.db.models.user import User
from app.services.life_events_service import LifeEventsService
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate, NotificationAudienceInput, AudienceType
from app.db.models.notification import NotificationPreference

logger = logging.getLogger(__name__)

async def generate_life_event_notifications():
    """
    Runs periodically to generate notifications for upcoming life events.
    """
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_active == True).all()
        life_events_service = LifeEventsService(db)
        notification_service = NotificationService(db)

        for user in users:
            prefs = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
            if not prefs or not prefs.in_app_enabled:
                continue

            # Get events for the next 7 days
            events = life_events_service.get_upcoming_events(user.id, days=7)
            for event in events:
                # Check preferences based on event_type
                if event.event_type == 'birthday' and not prefs.birthdays_enabled:
                    continue
                if event.event_type == 'anniversary' and not prefs.anniversaries_enabled:
                    continue
                if event.event_type == 'remembrance' and not prefs.remembrance_enabled:
                    continue
                if event.event_type == 'work_anniversary' and not prefs.work_anniversaries_enabled:
                    continue

                # To avoid spamming, only notify if the event is exactly 7 days away or today
                days_away = (event.start_date - datetime.utcnow().date()).days
                if days_away not in (0, 7):
                    continue

                timing_str = "Today" if days_away == 0 else "In 7 days"
                
                title = f"{timing_str}: {event.title}"
                body = event.description or f"Upcoming {event.event_type} for {event.title}"

                # Check if we already created a notification with this title for this user recently
                # (Simple deduplication by title and body)
                cutoff = datetime.utcnow() - timedelta(days=1)
                from app.db.models.notification import Notification, NotificationRecipient
                
                exists = db.query(Notification).join(NotificationRecipient).filter(
                    NotificationRecipient.user_id == user.id,
                    Notification.title == title,
                    Notification.created_at >= cutoff
                ).first()

                if not exists:
                    try:
                        audience = NotificationAudienceInput(
                            type=AudienceType.USER,
                            user_id=user.id
                        )
                        notif_create = NotificationCreate(
                            notification_type=event.event_type,
                            title=title,
                            body=body,
                            audience=audience
                        )
                        notification_service.create_notification(creator_user_id=None, data=notif_create)
                    except Exception as e:
                        logger.error(f"Failed to create notification for user {user.id}: {e}")

    except Exception as e:
        logger.error(f"Error generating life event notifications: {e}")
    finally:
        db.close()

async def life_event_scheduler():
    """
    Background task to run the life event notification generator once a day.
    """
    while True:
        logger.info("Running daily life event notification generation...")
        await generate_life_event_notifications()
        # Sleep for 24 hours
        await asyncio.sleep(24 * 60 * 60)
