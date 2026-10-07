import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models.family import Family, FamilyMember
from app.db.models.user import User

def test_album_crud(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    fam = Family(name="Test Fam", created_by_user_id=test_user.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, user_id=test_user.id, role="owner"))
    db_session.commit()
    
    # Create
    res = client.post("/api/v1/albums", headers=normal_user_token_headers, json={"family_id": str(fam.id), "title": "My Album"})
    assert res.status_code == 201
    album_id = res.json()["id"]
    
    # List
    res = client.get(f"/api/v1/albums?family_id={fam.id}", headers=normal_user_token_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1
    
    # Update
    res = client.patch(f"/api/v1/albums/{album_id}", headers=normal_user_token_headers, json={"description": "Nice"})
    assert res.status_code == 200
    assert res.json()["description"] == "Nice"
    
    # Delete
    res = client.delete(f"/api/v1/albums/{album_id}", headers=normal_user_token_headers)
    assert res.status_code == 204

def test_memory_crud(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    fam = Family(name="Test Fam", created_by_user_id=test_user.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, user_id=test_user.id, role="owner"))
    db_session.commit()
    
    res = client.post("/api/v1/memories", headers=normal_user_token_headers, json={"family_id": str(fam.id), "title": "My Memory", "body": "Story"})
    assert res.status_code == 201
    memory_id = res.json()["id"]
    
    res = client.get(f"/api/v1/memories/{memory_id}", headers=normal_user_token_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "My Memory"

def test_media_metadata(client: TestClient, db_session: Session, normal_user_token_headers: dict, test_user: User):
    fam = Family(name="Test Fam", created_by_user_id=test_user.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, user_id=test_user.id, role="owner"))
    db_session.commit()
    
    res = client.post("/api/v1/media", headers=normal_user_token_headers, json={
        "family_id": str(fam.id),
        "original_filename": "test.jpg",
        "mime_type": "image/jpeg"
    })
    assert res.status_code == 201
    media_id = res.json()["id"]
    
    res = client.get(f"/api/v1/media/{media_id}", headers=normal_user_token_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "pending"
