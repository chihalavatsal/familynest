from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "FamilyNest" in data["message"]


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "FamilyNest API"


def test_database_health_endpoint():
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "connected"
    assert "PostgreSQL" in data["database_engine"]
    assert "target" in data
    # Ensure credentials are not exposed
    assert "@" in data["target"]
    assert "****" in data["target"]
