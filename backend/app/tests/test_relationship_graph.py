"""Phase 6 — Relationship Graph API Test Suite.

Tests for read-only graph logic, path finding, BFS traversal, and derived kinship.
Ensures zero mutation to Families, People, or core relationships.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.relationship import Relationship
from app.core.security import get_password_hash, create_access_token


# =============================================================================
# Fixtures & Helpers
# =============================================================================







def _make_user(db_session) -> User:
    user = User(
        email=f"user_{uuid.uuid4().hex[:8]}@example.com",
        display_name="Test User",
        password_hash=get_password_hash("TestPassword123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {create_access_token(subject=str(user.id))}"}


def _make_person(db_session, user: User, first_name: str = "Test") -> Person:
    p = Person(first_name=first_name, last_name="P", created_by_user_id=user.id)
    db_session.add(p)
    db_session.flush()
    return p


def _make_rel(db_session, user: User, a: Person, b: Person, type_: str, is_current=True) -> Relationship:
    r = Relationship(person_a_id=a.id, person_b_id=b.id, relationship_type=type_, is_current=is_current, created_by_user_id=user.id)
    db_session.add(r)
    db_session.flush()
    return r


# =============================================================================
# Kinship & Path Tests
# =============================================================================

class TestGraphKinshipDerivations:
    
    def test_direct_kinships(self, client, db_session):
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        
        child = _make_person(db_session, user, "Child")
        parent = _make_person(db_session, user, "Parent")
        spouse = _make_person(db_session, user, "Spouse")
        guardian = _make_person(db_session, user, "Guardian")
        
        _make_rel(db_session, user, me, child, "parent")
        _make_rel(db_session, user, parent, me, "parent")
        _make_rel(db_session, user, me, spouse, "spouse")
        _make_rel(db_session, user, guardian, me, "guardian")
        db_session.commit()
        
        # Test Child -> my child
        r = client.get(f"/api/v1/relationships/how-related/{child.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "child"
        assert r["distance"] == 1
        
        # Test Parent -> my parent
        r = client.get(f"/api/v1/relationships/how-related/{parent.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "parent"
        
        # Test Spouse
        r = client.get(f"/api/v1/relationships/how-related/{spouse.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "spouse"
        
        # Test Guardian
        r = client.get(f"/api/v1/relationships/how-related/{guardian.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "guardian"

    def test_grandparent_derivation(self, client, db_session):
        user = _make_user(db_session)
        child = _make_person(db_session, user, "Child")
        child.claimed_by_user_id = user.id
        
        parent = _make_person(db_session, user, "Parent")
        grandparent = _make_person(db_session, user, "Grandparent")
        
        _make_rel(db_session, user, parent, child, "parent")
        _make_rel(db_session, user, grandparent, parent, "parent")
        db_session.commit()
        
        # Child checking how they relate to Grandparent (Child -> parent -> parent) -> grandparent
        r = client.get(f"/api/v1/relationships/how-related/{grandparent.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "grandparent"
        assert r["distance"] == 2

    def test_sibling_inference(self, client, db_session):
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        parent = _make_person(db_session, user, "Parent")
        bro = _make_person(db_session, user, "Brother")
        
        _make_rel(db_session, user, parent, me, "parent")
        _make_rel(db_session, user, parent, bro, "parent")
        db_session.commit()
        
        r = client.get(f"/api/v1/relationships/how-related/{bro.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "sibling"
        assert r["distance"] == 2
        
        # Explicit siblings endpoint
        sib_resp = client.get(f"/api/v1/people/{me.id}/siblings", headers=_auth_headers(user)).json()
        assert sib_resp["total"] == 1
        assert sib_resp["items"][0]["person"]["id"] == str(bro.id)

    def test_uncle_and_nephew(self, client, db_session):
        user = _make_user(db_session)
        uncle = _make_person(db_session, user, "Uncle")
        uncle.claimed_by_user_id = user.id
        parent = _make_person(db_session, user, "Parent")
        child = _make_person(db_session, user, "Child")
        
        _make_rel(db_session, user, parent, child, "parent")
        _make_rel(db_session, user, uncle, parent, "sibling") # Uncle is sibling of parent
        db_session.commit()
        
        # Uncle's perspective of Child: nephew/niece
        r = client.get(f"/api/v1/relationships/how-related/{child.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "nephew_or_niece"
        
        # Claim child instead
        uncle.claimed_by_user_id = None
        db_session.flush()
        child.claimed_by_user_id = user.id
        db_session.commit()
        
        # Child's perspective of Uncle: uncle/aunt
        r = client.get(f"/api/v1/relationships/how-related/{uncle.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "uncle_or_aunt"

    def test_cousin_derivation(self, client, db_session):
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        parent = _make_person(db_session, user, "Parent")
        aunt = _make_person(db_session, user, "Aunt")
        cousin = _make_person(db_session, user, "Cousin")
        
        _make_rel(db_session, user, parent, me, "parent")
        _make_rel(db_session, user, parent, aunt, "sibling")
        _make_rel(db_session, user, aunt, cousin, "parent")
        db_session.commit()
        
        r = client.get(f"/api/v1/relationships/how-related/{cousin.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "first_cousin"
        assert r["distance"] == 3


# =============================================================================
# Graph Constraints & Rules
# =============================================================================

class TestGraphEngineConstraints:
    
    def test_cycle_protection(self, client, db_session):
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        
        # Create a sibling loop (illogical but possible in DB)
        b = _make_person(db_session, user, "B")
        c = _make_person(db_session, user, "C")
        
        _make_rel(db_session, user, me, b, "sibling")
        _make_rel(db_session, user, b, c, "sibling")
        _make_rel(db_session, user, c, me, "sibling")
        db_session.commit()
        
        # Traversal shouldn't hang
        r = client.get(f"/api/v1/relationships/how-related/{c.id}", headers=_auth_headers(user)).json()
        assert r["distance"] == 1  # Should find direct path me->c instead of me->b->c
        assert r["relationship"] == "sibling"

    def test_historical_relationship_handling(self, client, db_session):
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        ex = _make_person(db_session, user, "Ex")
        
        _make_rel(db_session, user, me, ex, "spouse", is_current=False)
        db_session.commit()
        
        r = client.get(f"/api/v1/relationships/how-related/{ex.id}", headers=_auth_headers(user)).json()
        assert r["relationship"] == "former_spouse"  # Should fall back to historical connection
        
        # Explicitly ask for current direct relationships
        dr_current = client.get(f"/api/v1/people/{me.id}/relationships?include_historical=false", headers=_auth_headers(user)).json()
        assert dr_current["total"] == 0
        
        # But if we ask for direct relationships including historical
        dr = client.get(f"/api/v1/people/{me.id}/relationships?include_historical=true", headers=_auth_headers(user)).json()
        assert dr["total"] == 1
        assert dr["items"][0]["relationship"] == "former_spouse"

    def test_no_mutation_guarantee(self, client, db_session):
        """Crucial Phase 6 invariant: Graph engine is read-only."""
        user = _make_user(db_session)
        me = _make_person(db_session, user, "Me")
        me.claimed_by_user_id = user.id
        parent = _make_person(db_session, user, "Parent")
        grand = _make_person(db_session, user, "Grandparent")
        
        _make_rel(db_session, user, grand, parent, "parent")
        _make_rel(db_session, user, parent, me, "parent")
        db_session.commit()
        
        # Snapshot DB counts
        p_count = db_session.execute(select(func.count()).select_from(Person)).scalar_one()
        r_count = db_session.execute(select(func.count()).select_from(Relationship)).scalar_one()
        f_count = db_session.execute(select(func.count()).select_from(Family)).scalar_one()
        fm_count = db_session.execute(select(func.count()).select_from(FamilyMember)).scalar_one()
        
        # Execute expensive queries
        client.get(f"/api/v1/relationships/how-related/{grand.id}", headers=_auth_headers(user))
        client.get(f"/api/v1/people/{me.id}/ancestors", headers=_auth_headers(user))
        
        # Verify completely identical
        assert db_session.execute(select(func.count()).select_from(Person)).scalar_one() == p_count
        assert db_session.execute(select(func.count()).select_from(Relationship)).scalar_one() == r_count
        assert db_session.execute(select(func.count()).select_from(Family)).scalar_one() == f_count
        assert db_session.execute(select(func.count()).select_from(FamilyMember)).scalar_one() == fm_count

    def test_authorization_boundary(self, client, db_session):
        user1 = _make_user(db_session)
        p1 = _make_person(db_session, user1, "User1Person")
        p1.claimed_by_user_id = user1.id
        
        user2 = _make_user(db_session)
        p2 = _make_person(db_session, user2, "User2Person")
        p2.claimed_by_user_id = user2.id
        
        db_session.commit()
        
        # User 1 asks how they are related to User 2's person -> 404 (privacy preserving)
        resp = client.get(f"/api/v1/relationships/how-related/{p2.id}", headers=_auth_headers(user1))
        assert resp.status_code == 404
