"""Phase 4 — Family API Test Suite.

Tests:
- Family Creation, Listing, Detail, Update, Deletion
- Family Membership (Add, List, Role Update, Remove)
- Access Control (Owner, Admin, Member, Privacy-preserving 404s)
- Multi-Family Membership and Marriage Independence (No Relationships created)
"""
import uuid
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.relationship import Relationship
from app.db.models.audit_log import AuditLog
from app.core.security import get_password_hash, create_access_token


# =============================================================================
# Fixtures
# =============================================================================







# =============================================================================
# Helpers
# =============================================================================

def _make_user(db_session, *, email: str = None) -> User:
    email = email or f"user_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=email,
        display_name="Test User",
        password_hash=get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _auth_headers(user: User) -> dict:
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _make_person(db_session, *, claimed_by: User = None, first_name: str = "Test") -> Person:
    person = Person(
        first_name=first_name,
        last_name="Person",
        profile_status="claimed" if claimed_by else "unclaimed",
        claimed_by_user_id=claimed_by.id if claimed_by else None,
        created_by_user_id=claimed_by.id if claimed_by else None,
    )
    db_session.add(person)
    db_session.flush()
    return person


def _make_family(db_session, *, creator: User, name: str = "Test Family") -> Family:
    family = Family(
        name=name,
        description="A test family network",
        created_by_user_id=creator.id,
    )
    db_session.add(family)
    db_session.flush()
    return family


def _add_member(db_session, *, family: Family, person: Person, role: str = "member") -> FamilyMember:
    member = FamilyMember(
        family_id=family.id,
        person_id=person.id,
        role=role,
    )
    db_session.add(member)
    db_session.flush()
    return member


# =============================================================================
# Family Creation Tests
# =============================================================================

class TestFamilyCreate:
    
    def test_create_family_unauthenticated_rejected(self, client):
        resp = client.post("/api/v1/families", json={"name": "Patel Family"})
        assert resp.status_code == 401

    def test_create_family_no_claimed_person(self, client, db_session):
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/families",
            json={"name": "Patel Family"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Patel Family"
        assert data["created_by_user_id"] == str(user.id)
        assert data["member_count"] == 0
        
        # Verify no Person was created
        person_count = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
        assert person_count == 0

    def test_create_family_with_claimed_person(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, claimed_by=user, first_name="Ramesh")
        
        resp = client.post(
            "/api/v1/families",
            json={"name": "Patel Family"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["member_count"] == 1
        
        # Verify owner membership was created
        member = db_session.execute(
            select(FamilyMember).where(FamilyMember.family_id == uuid.UUID(data["id"]))
        ).scalar_one()
        assert member.person_id == person.id
        assert member.role == "owner"

    def test_create_family_validation(self, client, db_session):
        user = _make_user(db_session)
        
        # Empty name
        resp = client.post("/api/v1/families", json={"name": "   "}, headers=_auth_headers(user))
        assert resp.status_code == 422
        
        # Missing name
        resp = client.post("/api/v1/families", json={"description": "foo"}, headers=_auth_headers(user))
        assert resp.status_code == 422

    def test_create_family_audit_log(self, client, db_session):
        user = _make_user(db_session)
        resp = client.post("/api/v1/families", json={"name": "Audit Family"}, headers=_auth_headers(user))
        assert resp.status_code == 201
        family_id = resp.json()["id"]
        
        audit = db_session.execute(
            select(AuditLog).where(AuditLog.entity_id == uuid.UUID(family_id))
        ).scalar_one()
        assert audit.action == "family.create"
        assert audit.actor_user_id == user.id


# =============================================================================
# Family List Tests
# =============================================================================

class TestFamilyList:
    
    def test_list_accessible_only(self, client, db_session):
        user1 = _make_user(db_session)
        user2 = _make_user(db_session)
        
        # user1 creates family1
        f1 = _make_family(db_session, creator=user1, name="Family 1")
        # user2 creates family2
        f2 = _make_family(db_session, creator=user2, name="Family 2")
        
        resp = client.get("/api/v1/families", headers=_auth_headers(user1))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == str(f1.id)

    def test_list_as_member(self, client, db_session):
        creator = _make_user(db_session)
        member_user = _make_user(db_session)
        member_person = _make_person(db_session, claimed_by=member_user)
        
        f = _make_family(db_session, creator=creator, name="Shared Family")
        _add_member(db_session, family=f, person=member_person, role="member")
        
        # Member should see the family
        resp = client.get("/api/v1/families", headers=_auth_headers(member_user))
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["id"] == str(f.id)


# =============================================================================
# Family Detail & Update Tests
# =============================================================================

class TestFamilyDetailAndUpdate:
    
    def test_get_family_privacy(self, client, db_session):
        creator = _make_user(db_session)
        stranger = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        
        # Creator can get
        assert client.get(f"/api/v1/families/{f.id}", headers=_auth_headers(creator)).status_code == 200
        # Stranger gets 404 (privacy-preserving)
        assert client.get(f"/api/v1/families/{f.id}", headers=_auth_headers(stranger)).status_code == 404

    def test_patch_family_roles(self, client, db_session):
        creator = _make_user(db_session)
        creator_person = _make_person(db_session, claimed_by=creator)
        f = _make_family(db_session, creator=creator)
        _add_member(db_session, family=f, person=creator_person, role="owner")
        
        admin_user = _make_user(db_session)
        admin_person = _make_person(db_session, claimed_by=admin_user)
        _add_member(db_session, family=f, person=admin_person, role="admin")
        
        member_user = _make_user(db_session)
        member_person = _make_person(db_session, claimed_by=member_user)
        _add_member(db_session, family=f, person=member_person, role="member")
        
        payload = {"name": "Updated Name"}
        
        # Owner can patch
        resp = client.patch(f"/api/v1/families/{f.id}", json=payload, headers=_auth_headers(creator))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"
        
        # Admin can patch
        resp = client.patch(f"/api/v1/families/{f.id}", json={"name": "Admin Name"}, headers=_auth_headers(admin_user))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Admin Name"
        
        # Member cannot patch
        resp = client.patch(f"/api/v1/families/{f.id}", json={"name": "Hacked"}, headers=_auth_headers(member_user))
        assert resp.status_code == 403


# =============================================================================
# Family Delete Tests
# =============================================================================

class TestFamilyDelete:

    def test_delete_family_safety(self, client, db_session):
        creator = _make_user(db_session)
        creator_person = _make_person(db_session, claimed_by=creator)
        f = _make_family(db_session, creator=creator)
        _add_member(db_session, family=f, person=creator_person, role="owner")
        
        # Delete as owner
        resp = client.delete(f"/api/v1/families/{f.id}", headers=_auth_headers(creator))
        assert resp.status_code == 204
        
        # Verify family is gone
        assert db_session.execute(select(func.count()).select_from(Family)).scalar_one() == 0
        
        # Verify Person and User STILL EXIST
        assert db_session.execute(select(func.count()).select_from(Person)).scalar_one() == 1
        assert db_session.execute(select(func.count()).select_from(User)).scalar_one() == 1


# =============================================================================
# Membership Tests
# =============================================================================

class TestMembership:

    def test_add_member(self, client, db_session):
        creator = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        target_person = _make_person(db_session)
        
        resp = client.post(
            f"/api/v1/families/{f.id}/members",
            json={"person_id": str(target_person.id), "role": "member"},
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 201
        assert resp.json()["person_id"] == str(target_person.id)
        assert resp.json()["role"] == "member"
        
        # Verify NO relationship was created
        rel_count = db_session.execute(select(func.count()).select_from(Relationship)).scalar_one()
        assert rel_count == 0

    def test_duplicate_membership_rejected(self, client, db_session):
        creator = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        target_person = _make_person(db_session)
        _add_member(db_session, family=f, person=target_person)
        
        resp = client.post(
            f"/api/v1/families/{f.id}/members",
            json={"person_id": str(target_person.id), "role": "member"},
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 409

    def test_assign_owner_role_rejected(self, client, db_session):
        creator = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        target_person = _make_person(db_session)
        
        resp = client.post(
            f"/api/v1/families/{f.id}/members",
            json={"person_id": str(target_person.id), "role": "owner"},
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 422

    def test_list_members_privacy(self, client, db_session):
        creator = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        target_person = _make_person(db_session)
        _add_member(db_session, family=f, person=target_person)
        
        resp = client.get(f"/api/v1/families/{f.id}/members", headers=_auth_headers(creator))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        item = data["items"][0]
        # Should not expose email/phone
        assert "email" not in item
        assert "phone" not in item
        assert item["first_name"] == "Test"

    def test_update_member_role(self, client, db_session):
        creator = _make_user(db_session)
        f = _make_family(db_session, creator=creator)
        target_person = _make_person(db_session)
        _add_member(db_session, family=f, person=target_person, role="member")
        
        resp = client.patch(
            f"/api/v1/families/{f.id}/members/{target_person.id}",
            json={"role": "admin"},
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"
        
        # Try to upgrade to owner
        resp = client.patch(
            f"/api/v1/families/{f.id}/members/{target_person.id}",
            json={"role": "owner"},
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 422

    def test_remove_member(self, client, db_session):
        creator = _make_user(db_session)
        creator_person = _make_person(db_session, claimed_by=creator)
        f = _make_family(db_session, creator=creator)
        _add_member(db_session, family=f, person=creator_person, role="owner")
        
        target_person = _make_person(db_session)
        _add_member(db_session, family=f, person=target_person, role="member")
        
        resp = client.delete(
            f"/api/v1/families/{f.id}/members/{target_person.id}",
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 204
        
        # Target person still exists in DB
        assert db_session.execute(select(Person).where(Person.id == target_person.id)).scalar_one_or_none() is not None

    def test_remove_last_owner_rejected(self, client, db_session):
        creator = _make_user(db_session)
        creator_person = _make_person(db_session, claimed_by=creator)
        f = _make_family(db_session, creator=creator)
        _add_member(db_session, family=f, person=creator_person, role="owner")
        
        resp = client.delete(
            f"/api/v1/families/{f.id}/members/{creator_person.id}",
            headers=_auth_headers(creator),
        )
        assert resp.status_code == 409


# =============================================================================
# Marriage/Family-Network Independence Tests
# =============================================================================

class TestMultiFamilyAndIndependence:

    def test_person_in_multiple_families(self, client, db_session):
        creator = _make_user(db_session)
        f1 = _make_family(db_session, creator=creator, name="Family 1")
        f2 = _make_family(db_session, creator=creator, name="Family 2")
        
        person = _make_person(db_session, first_name="Multi")
        
        _add_member(db_session, family=f1, person=person)
        _add_member(db_session, family=f2, person=person)
        
        # Verify membership in both
        count = db_session.execute(
            select(func.count()).select_from(FamilyMember).where(FamilyMember.person_id == person.id)
        ).scalar_one()
        assert count == 2
        
        # Verify NO Relationships were magically created
        rel_count = db_session.execute(select(func.count()).select_from(Relationship)).scalar_one()
        assert rel_count == 0
