"""Phase 5 — Relationship API Test Suite.

Tests for creating and managing canonical relationships between people.
Strictly tests that relationships do not modify Family networks or People.
"""
import uuid
import pytest
from datetime import date
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


def _make_person(db_session, *, creator: User, first_name: str = "Test") -> Person:
    person = Person(
        first_name=first_name,
        last_name="Person",
        profile_status="unclaimed",
        created_by_user_id=creator.id,
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
# Creation & Validation Tests
# =============================================================================

class TestRelationshipCreate:
    
    def test_create_relationship_unauthenticated(self, client):
        resp = client.post("/api/v1/relationships", json={
            "person_a_id": str(uuid.uuid4()),
            "person_b_id": str(uuid.uuid4()),
            "relationship_type": "spouse"
        })
        assert resp.status_code == 401

    def test_create_relationship_success(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user, first_name="A")
        pb = _make_person(db_session, creator=user, first_name="B")
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pb.id),
                "relationship_type": "spouse"
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["relationship_type"] == "spouse"
        assert data["created_by_user_id"] == str(user.id)
        assert data["person_a"]["id"] == str(pa.id)
        assert data["person_b"]["id"] == str(pb.id)
        
        # Verify NO families were created or modified
        family_count = db_session.execute(select(func.count()).select_from(Family)).scalar_one()
        assert family_count == 0
        
        # Verify Audit Log
        audit = db_session.execute(
            select(AuditLog).where(AuditLog.entity_id == uuid.UUID(data["id"]))
        ).scalar_one()
        assert audit.action == "relationship.create"

    def test_missing_person_returns_404(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user, first_name="A")
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(uuid.uuid4()),
                "relationship_type": "spouse"
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 404

    def test_self_relationship_rejected(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pa.id),
                "relationship_type": "sibling"
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 422

    def test_date_validation(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pb.id),
                "relationship_type": "spouse",
                "start_date": "2020-01-01",
                "end_date": "2010-01-01" # End before start
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 422


class TestRelationshipTypes:

    @pytest.mark.parametrize("rel_type", [
        "parent", "child", "spouse", "divorced_spouse", "sibling", "guardian"
    ])
    def test_valid_types_accepted(self, client, db_session, rel_type):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pb.id),
                "relationship_type": rel_type
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 201

    def test_invalid_type_rejected(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pb.id),
                "relationship_type": "uncle"
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 422


# =============================================================================
# Duplicate & Symmetry Tests
# =============================================================================

class TestDuplicates:

    def test_duplicate_logical_relationship_rejected(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        payload = {
            "person_a_id": str(pa.id),
            "person_b_id": str(pb.id),
            "relationship_type": "spouse"
        }
        resp1 = client.post("/api/v1/relationships", json=payload, headers=_auth_headers(user))
        assert resp1.status_code == 201
        
        resp2 = client.post("/api/v1/relationships", json=payload, headers=_auth_headers(user))
        assert resp2.status_code == 409

    def test_symmetric_duplicate_rejected(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        client.post("/api/v1/relationships", json={
            "person_a_id": str(pa.id),
            "person_b_id": str(pb.id),
            "relationship_type": "sibling"
        }, headers=_auth_headers(user))
        
        # B sibling A is the same as A sibling B
        resp2 = client.post("/api/v1/relationships", json={
            "person_a_id": str(pb.id),
            "person_b_id": str(pa.id),
            "relationship_type": "sibling"
        }, headers=_auth_headers(user))
        assert resp2.status_code == 409


# =============================================================================
# Historical & Read/Update/Delete Tests
# =============================================================================

class TestHistoricalAndOperations:

    def test_historical_relationship(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={
                "person_a_id": str(pa.id),
                "person_b_id": str(pb.id),
                "relationship_type": "divorced_spouse",
                "start_date": "2010-01-01",
                "end_date": "2020-01-01",
                "is_current": False
            },
            headers=_auth_headers(user)
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["start_date"] == "2010-01-01"
        assert data["is_current"] is False

    def test_update_relationship_dates(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={"person_a_id": str(pa.id), "person_b_id": str(pb.id), "relationship_type": "spouse"},
            headers=_auth_headers(user)
        )
        rel_id = resp.json()["id"]
        
        patch_resp = client.patch(
            f"/api/v1/relationships/{rel_id}",
            json={"is_current": False, "end_date": "2023-01-01"},
            headers=_auth_headers(user)
        )
        assert patch_resp.status_code == 200
        data = patch_resp.json()
        assert data["is_current"] is False
        assert data["end_date"] == "2023-01-01"

    def test_delete_relationship(self, client, db_session):
        user = _make_user(db_session)
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        resp = client.post(
            "/api/v1/relationships",
            json={"person_a_id": str(pa.id), "person_b_id": str(pb.id), "relationship_type": "spouse"},
            headers=_auth_headers(user)
        )
        rel_id = resp.json()["id"]
        
        del_resp = client.delete(f"/api/v1/relationships/{rel_id}", headers=_auth_headers(user))
        assert del_resp.status_code == 204
        
        get_resp = client.get(f"/api/v1/relationships/{rel_id}", headers=_auth_headers(user))
        assert get_resp.status_code == 404
        
        # Verify people are preserved
        assert db_session.execute(select(func.count()).select_from(Person)).scalar_one() == 2


# =============================================================================
# Authorization & Independence Tests
# =============================================================================

class TestAuthorizationAndIndependence:

    def test_unauthorized_access_rejected(self, client, db_session):
        user_a = _make_user(db_session)
        pa = _make_person(db_session, creator=user_a)
        pb = _make_person(db_session, creator=user_a)
        rel_resp = client.post(
            "/api/v1/relationships",
            json={"person_a_id": str(pa.id), "person_b_id": str(pb.id), "relationship_type": "sibling"},
            headers=_auth_headers(user_a)
        )
        rel_id = rel_resp.json()["id"]
        
        user_b = _make_user(db_session)
        # B tries to get A's relationship
        assert client.get(f"/api/v1/relationships/{rel_id}", headers=_auth_headers(user_b)).status_code == 404
        # B tries to create relationship with A's person
        assert client.post("/api/v1/relationships", json={
            "person_a_id": str(pa.id),
            "person_b_id": str(pb.id),
            "relationship_type": "spouse"
        }, headers=_auth_headers(user_b)).status_code == 404

    def test_family_independence_no_auto_merge(self, client, db_session):
        """Crucial invariant: marriage does not merge families or create memberships."""
        user = _make_user(db_session)
        f1 = _make_family(db_session, creator=user, name="Family 1")
        f2 = _make_family(db_session, creator=user, name="Family 2")
        
        pa = _make_person(db_session, creator=user)
        pb = _make_person(db_session, creator=user)
        
        _add_member(db_session, family=f1, person=pa)
        _add_member(db_session, family=f2, person=pb)
        
        # Current state: 2 families, 2 memberships total
        assert db_session.execute(select(func.count()).select_from(FamilyMember)).scalar_one() == 2
        
        # Create a spouse relationship between A and B
        resp = client.post(
            "/api/v1/relationships",
            json={"person_a_id": str(pa.id), "person_b_id": str(pb.id), "relationship_type": "spouse"},
            headers=_auth_headers(user)
        )
        assert resp.status_code == 201
        
        # Families must remain separate. Memberships should still be exactly 2.
        assert db_session.execute(select(func.count()).select_from(FamilyMember)).scalar_one() == 2
        
        # A is only in Family 1
        m1 = db_session.execute(select(FamilyMember).where(FamilyMember.person_id == pa.id)).scalars().all()
        assert len(m1) == 1
        assert m1[0].family_id == f1.id
        
        # B is only in Family 2
        m2 = db_session.execute(select(FamilyMember).where(FamilyMember.person_id == pb.id)).scalars().all()
        assert len(m2) == 1
        assert m2[0].family_id == f2.id

    def test_list_relationships_network_access(self, client, db_session):
        """Test that a user can see relationships of people in their shared families."""
        user1 = _make_user(db_session)
        f1 = _make_family(db_session, creator=user1)
        
        # user1 creates pa, pb, and their relationship
        pa = _make_person(db_session, creator=user1)
        pb = _make_person(db_session, creator=user1)
        _add_member(db_session, family=f1, person=pa)
        
        rel = Relationship(person_a_id=pa.id, person_b_id=pb.id, relationship_type="sibling", created_by_user_id=user1.id)
        db_session.add(rel)
        db_session.flush()
        
        # user2 joins the family by claiming a person who is invited/added
        user2 = _make_user(db_session)
        pc = _make_person(db_session, creator=user2)
        pc.claimed_by_user_id = user2.id
        db_session.add(pc)
        _add_member(db_session, family=f1, person=pc)
        db_session.commit()
        
        # user2 should now be able to list relationships involving 'pa' because they share 'f1'
        resp = client.get(f"/api/v1/relationships?person_id={pa.id}", headers=_auth_headers(user2))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["person_a_id"] == str(pa.id)
