import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.invitation import Invitation
from app.db.models.person import Person
from app.db.models.user import User

def test_accept_invitation_by_id_success(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    # Setup person & invitation
    person = Person(first_name="Test", last_name="Claim", created_by_user_id=test_user.id)
    db_session.add(person)
    db_session.commit()
    
    other_user = User(email="other123@test.com", hashed_password="pw", is_active=True, first_name="O", last_name="U")
    db_session.add(other_user)
    db_session.commit()
    
    inv = Invitation(
        person_id=person.id,
        invited_by_user_id=other_user.id,
        invited_email=test_user.email,
        invitation_type="person_claim",
        invitation_token="token123",
        status="pending"
    )
    db_session.add(inv)
    db_session.commit()
    
    res = client.post(f"/api/v1/invitations/{inv.id}/accept", headers=normal_user_token_headers)
    assert res.status_code == 200, res.text
    assert res.json()["claimed"] is True
    
    db_session.refresh(person)
    assert person.claimed_by_user_id == test_user.id

def test_accept_invitation_by_id_unauthorized(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    person = Person(first_name="Test", last_name="Claim2", created_by_user_id=test_user.id)
    db_session.add(person)
    db_session.commit()
    
    inv = Invitation(
        person_id=person.id,
        invited_by_user_id=test_user.id,
        invited_email="wrong@test.com",
        invitation_type="person_claim",
        invitation_token="token456",
        status="pending"
    )
    db_session.add(inv)
    db_session.commit()
    
    res = client.post(f"/api/v1/invitations/{inv.id}/accept", headers=normal_user_token_headers)
    assert res.status_code == 403
