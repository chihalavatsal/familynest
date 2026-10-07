import pytest
from sqlalchemy import select
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.relationship import Relationship
from app.db.models.invitation import Invitation
from app.tests.conftest import client, db_session

def test_shared_family_scenario(client, db_session):
    # 1. User Vatsal registers
    vatsal_email = "vatsal@example.com"
    resp = client.post("/api/v1/auth/register", json={"email": vatsal_email, "password": "Password123!"})
    assert resp.status_code == 201
    
    # login Vatsal
    resp = client.post("/api/v1/auth/login", json={"email": vatsal_email, "password": "Password123!"})
    vatsal_token = resp.json()["access_token"]
    vatsal_headers = {"Authorization": f"Bearer {vatsal_token}"}
    
    # Vatsal creates his person profile (First onboarding step usually)
    resp = client.post("/api/v1/people", json={"first_name": "Vatsal"}, headers=vatsal_headers)
    vatsal_person_id = resp.json()["id"]
    
    # Claim it
    # For testing, we can manually claim since Vatsal just created it and it's his own
    vatsal_user = db_session.execute(select(User).where(User.email == vatsal_email)).scalar_one()
    vatsal_person = db_session.execute(select(Person).where(Person.id == vatsal_person_id)).scalar_one()
    vatsal_person.claimed_by_user_id = vatsal_user.id
    vatsal_person.profile_status = "claimed"
    db_session.commit()

    # Vatsal creates Chihala Family
    resp = client.post("/api/v1/families", json={"name": "Chihala Family"}, headers=vatsal_headers)
    family_id = resp.json()["id"]
    
    # Vatsal adds Father, Mother, Brother to DB (created_by = Vatsal)
    resp = client.post("/api/v1/people", json={"first_name": "Brother"}, headers=vatsal_headers)
    brother_person_id = resp.json()["id"]
    
    # Vatsal adds Brother to Chihala Family
    resp = client.post(f"/api/v1/families/{family_id}/members", json={"person_id": brother_person_id, "role": "member"}, headers=vatsal_headers)
    assert resp.status_code == 201
    
    # Vatsal adds relationship (Brother)
    resp = client.post("/api/v1/relationships", json={
        "person_a_id": vatsal_person_id,
        "person_b_id": brother_person_id,
        "relationship_type": "sibling"
    }, headers=vatsal_headers)
    assert resp.status_code == 201
    
    # 2. Vatsal invites Brother
    brother_email = "brother@example.com"
    resp = client.post(f"/api/v1/people/{brother_person_id}/invitations", json={
        "invited_email": brother_email,
        "invitation_type": "person_claim"
    }, headers=vatsal_headers)
    assert resp.status_code == 201
    inv_token = resp.json()["invitation_token"]
    
    # 3. Brother registers
    resp = client.post("/api/v1/auth/register", json={"email": brother_email, "password": "Password123!"})
    
    # Brother logs in
    resp = client.post("/api/v1/auth/login", json={"email": brother_email, "password": "Password123!"})
    brother_token = resp.json()["access_token"]
    brother_headers = {"Authorization": f"Bearer {brother_token}"}
    brother_user = db_session.execute(select(User).where(User.email == brother_email)).scalar_one()
    
    # Brother accepts invitation
    resp = client.post(f"/api/v1/invitations/{inv_token}/accept", headers=brother_headers)
    assert resp.status_code == 200
    
    # Verify canonical person
    # Brother User should now be claiming the original Brother person
    db_session.expire_all()
    b_person = db_session.execute(select(Person).where(Person.id == brother_person_id)).scalar_one()
    assert b_person.claimed_by_user_id == brother_user.id
    
    # Verify Brother sees the family
    resp = client.get("/api/v1/families", headers=brother_headers)
    assert resp.status_code == 200
    fams = resp.json()["items"]
    assert len(fams) == 1
    assert fams[0]["id"] == family_id
    
    # Verify Brother sees Vatsal
    resp = client.get("/api/v1/people", headers=brother_headers)
    assert resp.status_code == 200
    names = [p["first_name"] for p in resp.json()["items"]]
    assert "Vatsal" in names

def test_cross_family_isolation(client, db_session):
    # Setup User A (Chihala)
    resp = client.post("/api/v1/auth/register", json={"email": "a@ex.com", "password": "Password123!"})
    resp = client.post("/api/v1/auth/login", json={"email": "a@ex.com", "password": "Password123!"})
    a_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    
    # Setup User B (Patel)
    resp = client.post("/api/v1/auth/register", json={"email": "b@ex.com", "password": "Password123!"})
    resp = client.post("/api/v1/auth/login", json={"email": "b@ex.com", "password": "Password123!"})
    b_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    # A creates Family 1
    resp = client.post("/api/v1/families", json={"name": "Family 1"}, headers=a_headers)
    f1_id = resp.json()["id"]

    # B creates Family 2
    resp = client.post("/api/v1/families", json={"name": "Family 2"}, headers=b_headers)
    f2_id = resp.json()["id"]

    # A adds Person C to Family 1
    resp = client.post("/api/v1/people", json={"first_name": "Person C"}, headers=a_headers)
    c_id = resp.json()["id"]
    client.post(f"/api/v1/families/{f1_id}/members", json={"person_id": c_id, "role": "member"}, headers=a_headers)

    # A cannot see Family 2
    resp = client.get(f"/api/v1/families/{f2_id}", headers=a_headers)
    assert resp.status_code == 404

    # B cannot see Person C
    resp = client.get(f"/api/v1/people/{c_id}", headers=b_headers)
    assert resp.status_code == 404
