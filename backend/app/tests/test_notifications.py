"""Tests for Phase 8: Notifications."""
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.notification import Notification, NotificationRecipient
from app.core.security import get_password_hash, create_access_token





def _make_user(db, email):
    u = User(email=email, password_hash=get_password_hash("pass"), display_name="U")
    db.add(u)
    db.flush()
    return u

def _make_person(db, user, first_name="A"):
    p = Person(first_name=first_name, last_name="Z", created_by_user_id=user.id, claimed_by_user_id=user.id, profile_status="claimed")
    db.add(p)
    db.flush()
    return p
    
def _make_unclaimed_person(db, creator, first_name="B"):
    p = Person(first_name=first_name, last_name="Z", created_by_user_id=creator.id, claimed_by_user_id=None, profile_status="unclaimed")
    db.add(p)
    db.flush()
    return p

def _make_family(db, owner_person):
    f = Family(name="Test Family", description="", created_by_user_id=owner_person.claimed_by_user_id)
    db.add(f)
    db.flush()
    fm = FamilyMember(family_id=f.id, person_id=owner_person.id, role="owner")
    db.add(fm)
    db.flush()
    return f

def _add_member(db, family, person, role="member"):
    fm = FamilyMember(family_id=family.id, person_id=person.id, role=role)
    db.add(fm)
    db.flush()

def _auth_headers(user):
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}

class TestNotifications:
    def test_create_family_notification(self, client, db_session):
        u1 = _make_user(db_session, "u1@e.com")
        p1 = _make_person(db_session, u1)
        u2 = _make_user(db_session, "u2@e.com")
        p2 = _make_person(db_session, u2)
        
        f = _make_family(db_session, p1)
        _add_member(db_session, f, p2)
        
        db_session.commit()
        
        # u1 creates notification for family
        resp = client.post(
            "/api/v1/notifications",
            headers=_auth_headers(u1),
            json={
                "notification_type": "family_update",
                "title": "Hello Family",
                "body": "Welcome",
                "audience": {
                    "type": "family",
                    "family_id": str(f.id)
                }
            }
        )
        assert resp.status_code == 201
        
        # Verify recipients are u1 and u2
        recipients = db_session.execute(select(NotificationRecipient.user_id)).scalars().all()
        assert set(recipients) == {u1.id, u2.id}
        
    def test_marriage_isolation(self, client, db_session):
        u1 = _make_user(db_session, "u1@e.com")
        p1 = _make_person(db_session, u1)
        
        u2 = _make_user(db_session, "u2@e.com")
        p2 = _make_person(db_session, u2)
        
        f_father = _make_family(db_session, p1)
        f_mother = _make_family(db_session, p2)
        # They are separate families. We simulate marriage just by having two families
        
        db_session.commit()
        
        # u1 targets f_father
        resp = client.post(
            "/api/v1/notifications",
            headers=_auth_headers(u1),
            json={
                "notification_type": "family_update",
                "title": "Hello Father side",
                "body": "Hi",
                "audience": {
                    "type": "family",
                    "family_id": str(f_father.id)
                }
            }
        )
        assert resp.status_code == 201
        
        recipients = db_session.execute(select(NotificationRecipient.user_id)).scalars().all()
        assert set(recipients) == {u1.id}  # u2 not in father family
        
    def test_selected_members_with_unclaimed(self, client, db_session):
        u1 = _make_user(db_session, "u1@e.com")
        p1 = _make_person(db_session, u1)
        
        u2 = _make_user(db_session, "u2@e.com")
        p2 = _make_person(db_session, u2)
        
        # Unclaimed person created by u1
        p_unclaimed = _make_unclaimed_person(db_session, u1)
        
        db_session.commit()
        
        # u1 targets p2 and p_unclaimed. Wait! u1 doesn't have access to p2 unless they are in same family
        f = _make_family(db_session, p1)
        _add_member(db_session, f, p2)
        db_session.commit()
        
        resp = client.post(
            "/api/v1/notifications",
            headers=_auth_headers(u1),
            json={
                "notification_type": "family_update",
                "title": "Selected",
                "body": "Hi",
                "audience": {
                    "type": "selected_members",
                    "person_ids": [str(p2.id), str(p_unclaimed.id)]
                }
            }
        )
        assert resp.status_code == 201
        
        # Recipient should only be u2! Unclaimed person gets NO user notification row.
        recipients = db_session.execute(select(NotificationRecipient.user_id)).scalars().all()
        assert set(recipients) == {u2.id}
        
    def test_read_unread_list(self, client, db_session):
        u1 = _make_user(db_session, "u1@e.com")
        p1 = _make_person(db_session, u1)
        db_session.commit()
        
        resp = client.post(
            "/api/v1/notifications",
            headers=_auth_headers(u1),
            json={
                "notification_type": "system",
                "title": "Hello",
                "body": "World",
                "audience": {
                    "type": "user",
                    "user_id": str(u1.id)
                }
            }
        ).json()
        nid = resp["id"]
        
        # List unread
        res = client.get("/api/v1/notifications?unread=true", headers=_auth_headers(u1)).json()
        assert res["total"] == 1
        
        # Mark read
        client.post(f"/api/v1/notifications/{nid}/read", headers=_auth_headers(u1))
        
        # List unread again
        res = client.get("/api/v1/notifications?unread=true", headers=_auth_headers(u1)).json()
        assert res["total"] == 0
        
        # List all
        res = client.get("/api/v1/notifications?unread=false", headers=_auth_headers(u1)).json()
        assert res["total"] == 1
        
    def test_bulk_read(self, client, db_session):
        u1 = _make_user(db_session, "u1@e.com")
        db_session.commit()
        
        for _ in range(3):
            client.post(
                "/api/v1/notifications",
                headers=_auth_headers(u1),
                json={
                    "notification_type": "system",
                    "title": "Hello",
                    "body": "World",
                    "audience": {
                        "type": "user",
                        "user_id": str(u1.id)
                    }
                }
            )
            
        res = client.get("/api/v1/notifications?unread=true", headers=_auth_headers(u1)).json()
        assert res["total"] == 3
        
        client.post("/api/v1/notifications/read-all", headers=_auth_headers(u1))
        
        res = client.get("/api/v1/notifications?unread=true", headers=_auth_headers(u1)).json()
        assert res["total"] == 0
