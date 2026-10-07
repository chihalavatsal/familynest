import re

with open("app/services/notification_service.py", "r") as f:
    content = f.read()

replacement = """    def _build_response(self, notification: Notification, is_read: bool) -> NotificationResponse:
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
        )"""

content = re.sub(
    r"    def _build_response\(self, notification: Notification, is_read: bool\) -> NotificationResponse:\n.*?created_at=notification\.created_at\n\s*\)",
    replacement,
    content,
    flags=re.DOTALL
)

with open("app/services/notification_service.py", "w") as f:
    f.write(content)
