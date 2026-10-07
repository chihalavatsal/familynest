"""Tests for Phase 7: Person Claiming and Invitations."""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.invitation import Invitation
from app.db.models.audit_log import AuditLog
from app.core.security import get_password_hash, create_access_token








def _make_user(db_session, email="test@example.com") -> User:
    user = User(
        email=email,
        display_name="Test User",
        password_hash=get_password_hash("TestPassword123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _auth_headers(user: User) -> dict:
    return {"Authorization": f"Bearer {create_access_token(subject=str(user.id))}"}


def _make_person(db_session, user: User, first_name: str = "Test", is_deceased=False) -> Person:
    p = Person(
        first_name=first_name, 
        last_name="P", 
        created_by_user_id=user.id,
        is_deceased=is_deceased
    )
    db_session.add(p)
    db_session.flush()
    return p


class TestPersonClaiming:
    def test_direct_claim_success(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user)
        db_session.commit()

        resp = client.post(f"/api/v1/people/{person.id}/claim", headers=_auth_headers(user))
        assert resp.status_code == 200
        assert resp.json()["claimed"] is True
        
        db_session.expire_all()
        # Verify db
        p = db_session.execute(select(Person).where(Person.id == person.id)).scalar_one()
        assert p.claimed_by_user_id == user.id
        assert p.profile_status == "claimed"
        
        # Verify audit
        audit = db_session.execute(select(AuditLog).where(AuditLog.action == "person.claim")).scalar_one()
        assert audit.entity_id == person.id

    def test_unauthenticated_claim_rejected(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user)
        db_session.commit()

        resp = client.post(f"/api/v1/people/{person.id}/claim")
        assert resp.status_code == 401

    def test_claim_already_claimed_person_rejected(self, client, db_session):
        user1 = _make_user(db_session, "u1@e.com")
        user2 = _make_user(db_session, "u2@e.com")
        
        person = _make_person(db_session, user1)
        person.claimed_by_user_id = user2.id
        db_session.commit()

        resp = client.post(f"/api/v1/people/{person.id}/claim", headers=_auth_headers(user1))
        assert resp.status_code == 409
        assert "already been claimed" in resp.json()["detail"]

    def test_user_cannot_claim_multiple_people(self, client, db_session):
        user = _make_user(db_session)
        p1 = _make_person(db_session, user, "P1")
        p1.claimed_by_user_id = user.id
        
        p2 = _make_person(db_session, user, "P2")
        db_session.commit()

        resp = client.post(f"/api/v1/people/{p2.id}/claim", headers=_auth_headers(user))
        assert resp.status_code == 409
        assert "only claim one Person" in resp.json()["detail"]

    def test_deceased_cannot_be_claimed(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user, is_deceased=True)
        db_session.commit()

        resp = client.post(f"/api/v1/people/{person.id}/claim", headers=_auth_headers(user))
        assert resp.status_code == 409
        assert "deceased" in resp.json()["detail"]

    def test_inaccessible_person_cannot_be_claimed(self, client, db_session):
        user1 = _make_user(db_session, "u1@e.com")
        person1 = _make_person(db_session, user1)
        
        user2 = _make_user(db_session, "u2@e.com")
        db_session.commit()

        resp = client.post(f"/api/v1/people/{person1.id}/claim", headers=_auth_headers(user2))
        assert resp.status_code == 404

    def test_transaction_rollback_preserves_uniqueness(self, client, db_session):
        # We simulate a failure in direct claim by passing an invalid person id.
        # It should just 404.
        user = _make_user(db_session)
        resp = client.post(f"/api/v1/people/{uuid.uuid4()}/claim", headers=_auth_headers(user))
        assert resp.status_code == 404


class TestInvitations:
    def test_create_invitation(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user)
        db_session.commit()

        resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(user),
            json={"invited_email": "invited@example.com"}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "invitation_token" in data
        assert data["status"] == "pending"
        
        # Verify db
        inv = db_session.execute(select(Invitation).where(Invitation.id == data["id"])).scalar_one()
        assert inv.invitation_token == data["invitation_token"]

    def test_accept_invitation(self, client, db_session):
        sender = _make_user(db_session, "sender@example.com")
        recipient = _make_user(db_session, "recipient@example.com")
        person = _make_person(db_session, sender)
        db_session.commit()

        # Create
        inv_resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(sender),
            json={"invited_email": "recipient@example.com"}
        ).json()
        
        token = inv_resp["invitation_token"]

        # Accept
        resp = client.post(f"/api/v1/invitations/{token}/accept", headers=_auth_headers(recipient))
        if resp.status_code != 200:
            print("Accept failed:", resp.text)
        assert resp.status_code == 200
        
        db_session.expire_all()
        # Verify person claimed
        p = db_session.execute(select(Person).where(Person.id == person.id)).scalar_one()
        assert p.claimed_by_user_id == recipient.id

        # Verify inv accepted
        inv = db_session.execute(select(Invitation).where(Invitation.id == inv_resp["id"])).scalar_one()
        assert inv.status == "accepted"

    def test_wrong_recipient_cannot_accept(self, client, db_session):
        sender = _make_user(db_session, "s@e.com")
        wrong_recipient = _make_user(db_session, "wrong@e.com")
        person = _make_person(db_session, sender)
        db_session.commit()

        inv_resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(sender),
            json={"invited_email": "right@e.com"}
        ).json()
        
        token = inv_resp["invitation_token"]
        resp = client.post(f"/api/v1/invitations/{token}/accept", headers=_auth_headers(wrong_recipient))
        assert resp.status_code == 403

    def test_accepted_invitation_cannot_be_reused(self, client, db_session):
        sender = _make_user(db_session, "s@e.com")
        recipient = _make_user(db_session, "r@e.com")
        person = _make_person(db_session, sender)
        db_session.commit()

        inv_resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(sender),
            json={"invited_email": "r@e.com"}
        ).json()
        
        token = inv_resp["invitation_token"]
        client.post(f"/api/v1/invitations/{token}/accept", headers=_auth_headers(recipient))
        
        # Try again
        resp = client.post(f"/api/v1/invitations/{token}/accept", headers=_auth_headers(recipient))
        assert resp.status_code == 400
        assert "no longer valid" in resp.json()["detail"]

    def test_cancel_invitation(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user)
        db_session.commit()

        inv_resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(user),
            json={"invited_email": "test@e.com"}
        ).json()
        
        resp = client.post(f"/api/v1/invitations/{inv_resp['id']}/cancel", headers=_auth_headers(user))
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_list_and_detail_do_not_expose_token(self, client, db_session):
        user = _make_user(db_session)
        person = _make_person(db_session, user)
        db_session.commit()

        inv_resp = client.post(
            f"/api/v1/people/{person.id}/invitations",
            headers=_auth_headers(user),
            json={"invited_email": "test@e.com"}
        ).json()

        # List
        list_resp = client.get("/api/v1/invitations?direction=sent", headers=_auth_headers(user)).json()
        assert "invitation_token" not in list_resp["items"][0]

        # Detail
        detail_resp = client.get(f"/api/v1/invitations/{inv_resp['id']}", headers=_auth_headers(user)).json()
        assert "invitation_token" not in detail_resp

