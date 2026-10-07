import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.family import Family, FamilyMember
from app.db.models.user import User

def test_family_privacy_settings(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    fam = Family(name="Privacy Fam", created_by_user_id=test_user.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, user_id=test_user.id, role="owner"))
    db_session.commit()
    
    # Get settings
    res = client.get(f"/api/v1/families/{fam.id}/settings", headers=normal_user_token_headers)
    assert res.status_code == 200
    assert res.json()["allow_member_discovery"] == True
    
    # Update settings
    res = client.patch(f"/api/v1/families/{fam.id}/settings", headers=normal_user_token_headers, json={"allow_member_discovery": False})
    assert res.status_code == 200
    assert res.json()["allow_member_discovery"] == False

def test_memory_audience(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    fam = Family(name="Audience Fam", created_by_user_id=test_user.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, user_id=test_user.id, role="owner"))
    db_session.commit()
    
    res = client.post("/api/v1/memories", headers=normal_user_token_headers, json={
        "family_id": str(fam.id), 
        "title": "Secret Memory", 
        "body": "Shh",
        "visibility": "selected_members",
        "allowed_user_ids": [str(test_user.id)]
    })
    assert res.status_code == 201
    mem_id = res.json()["id"]
    
    res = client.get(f"/api/v1/memories/{mem_id}", headers=normal_user_token_headers)
    assert res.status_code == 200
