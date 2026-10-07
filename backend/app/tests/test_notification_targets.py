import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.notification import Notification, NotificationTarget, NotificationRecipient
from app.db.models.user import User

def test_notification_with_family_target(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    notif = Notification(notification_type="family_update", title="T", body="B")
    db_session.add(notif)
    db_session.commit()
    
    fam_id = uuid.uuid4()
    target = NotificationTarget(notification_id=notif.id, audience_type="family", family_id=fam_id)
    recip = NotificationRecipient(notification_id=notif.id, user_id=test_user.id)
    db_session.add_all([target, recip])
    db_session.commit()
    
    res = client.get(f"/api/v1/notifications/{notif.id}", headers=normal_user_token_headers)
    assert res.status_code == 200, res.text
    assert res.json()["target_type"] == "family"
    assert res.json()["target_id"] == str(fam_id)

def test_notification_with_no_target(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    notif = Notification(notification_type="general", title="T", body="B")
    db_session.add(notif)
    db_session.commit()
    
    target = NotificationTarget(notification_id=notif.id, audience_type="user")
    recip = NotificationRecipient(notification_id=notif.id, user_id=test_user.id)
    db_session.add_all([target, recip])
    db_session.commit()
    
    res = client.get(f"/api/v1/notifications/{notif.id}", headers=normal_user_token_headers)
    assert res.status_code == 200, res.text
    assert res.json()["target_type"] is None
    assert res.json()["target_id"] is None

@pytest.mark.skip(reason="Database contract gap discovered: NotificationTarget lacks event_id")
def test_notification_with_event_target(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    pass

@pytest.mark.skip(reason="Database contract gap discovered: NotificationTarget lacks invitation_id")
def test_notification_with_invitation_target(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    pass
