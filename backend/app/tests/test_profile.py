import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
import uuid

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.privacy import PersonPrivacySettings
from app.core.security import get_password_hash, create_access_token






@pytest.fixture
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

def test_get_current_profile_unclaimed(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    token = create_access_token(u.id)
    r = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["user"]["email"] == u.email
    assert data["person"] is None

def test_get_current_profile_claimed(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    p = Person(first_name="Claimed", claimed_by_user_id=u.id)
    db_session.add(p)
    db_session.commit()
    
    token = create_access_token(u.id)
    r = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["person"]["first_name"] == "Claimed"

def test_update_person_profile(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    p = Person(first_name="Old", claimed_by_user_id=u.id)
    db_session.add(p)
    db_session.commit()
    
    token = create_access_token(u.id)
    r = client.patch("/api/v1/profile/person", json={"first_name": "New", "date_of_birth": "1990-01-01"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["first_name"] == "New"
    assert data["date_of_birth"] == "1990-01-01"

def test_privacy_settings(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    p = Person(first_name="Test", claimed_by_user_id=u.id)
    db_session.add(p)
    db_session.commit()
    
    token = create_access_token(u.id)
    # Get defaults
    r = client.get("/api/v1/profile/privacy", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["phone_visibility"] == "private"
    
    # Update
    r2 = client.patch("/api/v1/profile/privacy", json={"phone_visibility": "family"}, headers={"Authorization": f"Bearer {token}"})
    print(r2.json())
    assert r2.status_code == 200
    assert r2.json()["phone_visibility"] == "family"

def test_dashboard_and_completeness(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    p = Person(first_name="Dash", last_name="Board", claimed_by_user_id=u.id)
    db_session.add(p)
    f = Family(name="My Fam", created_by_user_id=u.id)
    db_session.add(f)
    db_session.commit()
    
    db_session.add(FamilyMember(family_id=f.id, person_id=p.id, role="owner"))
    db_session.commit()
    
    token = create_access_token(u.id)
    
    # Completeness
    r = client.get("/api/v1/profile/completeness", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    comp = r.json()
    assert "first_name" in comp["completed"]
    assert "date_of_birth" in comp["missing"]
    
    # Dashboard
    r2 = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    print(r2.json())
    assert r2.status_code == 200
    dash = r2.json()
    assert dash["profile"]["first_name"] == "Dash"
    assert len(dash["families"]) == 1
    assert dash["families"][0]["name"] == "My Fam"
    assert dash["families"][0]["member_count"] == 1
    assert "upcoming_events" in dash
    assert "recent_activity" in dash

def test_family_overview(client: TestClient, db_session: Session, test_users):
    u = test_users[0]
    p = Person(first_name="Dash", last_name="Board", claimed_by_user_id=u.id)
    db_session.add(p)
    f = Family(name="My Fam", created_by_user_id=u.id)
    db_session.add(f)
    db_session.commit()
    
    db_session.add(FamilyMember(family_id=f.id, person_id=p.id, role="owner"))
    db_session.commit()
    
    token = create_access_token(u.id)
    r = client.get(f"/api/v1/families/{f.id}/overview", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["name"] == "My Fam"
    assert r.json()["member_count"] == 1


def test_privacy_resolver(client: TestClient, db_session: Session, test_users):
    user_owner, user_stranger, user_family = test_users
    
    # User Owner's Person
    p_owner = Person(first_name="Owner", phone="123", email="o@o.com", claimed_by_user_id=user_owner.id)
    # User Family's Person
    p_family = Person(first_name="Fam", claimed_by_user_id=user_family.id)
    # User Stranger's Person
    p_stranger = Person(first_name="Str", claimed_by_user_id=user_stranger.id)
    db_session.add_all([p_owner, p_family, p_stranger])
    db_session.commit()
    
    # Settings for Owner
    settings = PersonPrivacySettings(person_id=p_owner.id, phone_visibility="private", email_visibility="family", bio_visibility="public")
    db_session.add(settings)
    
    # Family network
    f = Family(name="Shared Fam", created_by_user_id=user_owner.id)
    db_session.add(f)
    db_session.commit()
    
    db_session.add(FamilyMember(family_id=f.id, person_id=p_owner.id, role="owner"))
    db_session.add(FamilyMember(family_id=f.id, person_id=p_family.id, role="member"))
    db_session.commit()
    
    from app.services.privacy_service import PrivacyService
    svc = PrivacyService(db_session)
    
    # Owner views own
    own_summary = svc.resolve_safe_person(p_owner, user_owner.id)
    assert own_summary.phone == "123"
    assert own_summary.email == "o@o.com"
    
    # Stranger views owner
    stranger_summary = svc.resolve_safe_person(p_owner, user_stranger.id)
    assert stranger_summary.phone is None
    assert stranger_summary.email is None
    
    # Family views owner
    family_summary = svc.resolve_safe_person(p_owner, user_family.id)
    assert family_summary.phone is None # private
    assert family_summary.email == "o@o.com" # family
