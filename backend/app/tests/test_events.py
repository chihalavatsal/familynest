import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, date
import uuid

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.event import Event, EventTarget, EventParticipant
from app.db.models.activity import Activity
from app.core.security import get_password_hash, create_access_token






def test_users(db_session):
    users = []
    for i in range(3):
        u = User(
            email=f"user_{uuid.uuid4().hex[:8]}@example.com",
            password_hash=get_password_hash("password"),
            display_name="Test User",
            is_active=True
        )
        db_session.add(u)
        users.append(u)
    db_session.commit()
    return users


def user_token_headers(test_users):
    u = test_users[0]
    token = create_access_token(u.id)
    return {"Authorization": f"Bearer {token}"}, u

def test_event_create_and_activity(client: TestClient, db_session: Session, user_token_headers):
    headers, user = user_token_headers
    db = db_session
    
    # Create family and person
    person = Person(first_name="Event Creator", claimed_by_user_id=user.id)
    db.add(person)
    db.commit()
    db.refresh(person)
    
    family = Family(name="Test Event Family", created_by_user_id=user.id)
    db.add(family)
    db.commit()
    db.refresh(family)
    
    db.add(FamilyMember(family_id=family.id, person_id=person.id, role="owner"))
    db.commit()
    
    event_data = {
        "event_type": "family_event",
        "title": "Test Family Event",
        "description": "Desc",
        "start_datetime": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "end_datetime": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "all_day": False,
        "audience": {
            "type": "family",
            "family_id": str(family.id)
        }
    }
    
    r = client.post("/api/v1/events", json=event_data, headers=headers)
    assert r.status_code == 201
    resp = r.json()
    assert resp["title"] == "Test Family Event"
    event_id = resp["id"]
    
    # Verify Activity was created
    act_r = client.get(f"/api/v1/activity?family_id={family.id}", headers=headers)
    assert act_r.status_code == 200
    activities = act_r.json()
    assert len(activities) > 0
    assert any(a["activity_type"] == "family_event.created" and a["entity_id"] == event_id for a in activities)

def test_event_isolation_families(client: TestClient, db_session: Session, test_users):
    user1, user2 = test_users[:2]
    db = db_session
    
    # Setup users and families
    p1 = Person(first_name="U1", claimed_by_user_id=user1.id)
    p2 = Person(first_name="U2", claimed_by_user_id=user2.id)
    db.add_all([p1, p2])
    db.commit()
    
    f1 = Family(name="F1", created_by_user_id=user1.id)
    f2 = Family(name="F2", created_by_user_id=user2.id)
    db.add_all([f1, f2])
    db.commit()
    
    db.add(FamilyMember(family_id=f1.id, person_id=p1.id, role="owner"))
    db.add(FamilyMember(family_id=f2.id, person_id=p2.id, role="owner"))
    db.commit()
    
    # User 1 creates event for F1
    token1 = create_access_token(user1.id)
    h1 = {"Authorization": f"Bearer {token1}"}
    
    client.post("/api/v1/events", json={
        "event_type": "family_event",
        "title": "E1",
        "start_datetime": datetime.now(timezone.utc).isoformat(),
        "end_datetime": datetime.now(timezone.utc).isoformat(),
        "audience": {"type": "family", "family_id": str(f1.id)}
    }, headers=h1)
    
    token2 = create_access_token(user2.id)
    h2 = {"Authorization": f"Bearer {token2}"}
    
    # User 2 creates event for F2
    client.post("/api/v1/events", json={
        "event_type": "family_event",
        "title": "E2",
        "start_datetime": datetime.now(timezone.utc).isoformat(),
        "end_datetime": datetime.now(timezone.utc).isoformat(),
        "audience": {"type": "family", "family_id": str(f2.id)}
    }, headers=h2)
    
    # User 1 should only see E1
    r1 = client.get("/api/v1/events", headers=h1)
    e1_list = r1.json()
    assert len(e1_list) == 1
    assert e1_list[0]["title"] == "E1"
    
    # User 2 should only see E2
    r2 = client.get("/api/v1/events", headers=h2)
    e2_list = r2.json()
    assert len(e2_list) == 1
    assert e2_list[0]["title"] == "E2"
    
def test_event_birthday(client: TestClient, db_session: Session, user_token_headers):
    headers, user = user_token_headers
    db = db_session
    
    p = Person(first_name="Bday Person", date_of_birth=date(1990, 1, 1), created_by_user_id=user.id)
    db.add(p)
    db.commit()
    
    event_data = {
        "event_type": "birthday",
        "title": "Bday",
        "start_date": "2026-01-01",
        "end_date": "2026-01-01",
        "all_day": True,
        "person_id": str(p.id),
        "audience": {
            "type": "user",
            "user_id": str(user.id)
        }
    }
    r = client.post("/api/v1/events", json=event_data, headers=headers)
    assert r.status_code == 201
    resp = r.json()
    assert resp["person_id"] == str(p.id)
    assert resp["all_day"] is True
    
def test_event_unclaimed_participant(client: TestClient, db_session: Session, user_token_headers):
    headers, user = user_token_headers
    db = db_session
    
    # Unclaimed person
    p = Person(first_name="Uncle", created_by_user_id=user.id)
    db.add(p)
    db.commit()
    
    event_data = {
        "event_type": "family_event",
        "title": "Gathering",
        "start_datetime": datetime.now(timezone.utc).isoformat(),
        "end_datetime": datetime.now(timezone.utc).isoformat(),
        "audience": {"type": "user", "user_id": str(user.id)}
    }
    r = client.post("/api/v1/events", json=event_data, headers=headers)
    ev_id = r.json()["id"]
    
    # Add participant
    r2 = client.post(f"/api/v1/events/{ev_id}/participants?person_id={p.id}", headers=headers)
    assert r2.status_code == 201
    
    # Duplicate participant
    r3 = client.post(f"/api/v1/events/{ev_id}/participants?person_id={p.id}", headers=headers)
    assert r3.status_code == 400
    
def test_event_update_authorization(client: TestClient, db_session: Session, test_users):
    user1, user2 = test_users[:2]
    db = db_session
    
    h1 = {"Authorization": f"Bearer {create_access_token(user1.id)}"}
    h2 = {"Authorization": f"Bearer {create_access_token(user2.id)}"}
    
    r = client.post("/api/v1/events", json={
        "event_type": "important_date",
        "title": "U1 Event",
        "start_datetime": datetime.now(timezone.utc).isoformat(),
        "end_datetime": datetime.now(timezone.utc).isoformat(),
        "audience": {"type": "user", "user_id": str(user1.id)}
    }, headers=h1)
    ev_id = r.json()["id"]
    
    # User 2 tries to update
    r2 = client.patch(f"/api/v1/events/{ev_id}", json={"title": "Hacked"}, headers=h2)
    assert r2.status_code == 404 # User 2 cannot access event
