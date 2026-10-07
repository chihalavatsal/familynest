"""Comprehensive Authentication & Security Test Suite for FamilyNest.

Tests:
1. Registration (valid, duplicate, invalid email, short password, long password, whitespace password)
2. User/Person Architecture Rule (assert registration does NOT create a Person record)
3. Login (correct credentials, wrong password, unknown email, inactive user)
4. JWT Tokens (valid access, expired access, invalid signature, wrong token type, malformed)
5. Refresh Tokens (valid refresh, access token rejected as refresh token, invalid refresh, expired refresh)
6. Current User /me (authenticated, missing token, invalid token, inactive user)
7. Logout (behavior and response verification)
8. Security (plaintext password never stored, password_hash never returned, secrets never exposed)
"""
import uuid
import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)








# ==============================================================================
# 1. REGISTRATION TESTS
# ==============================================================================

def test_register_valid_user(client, db_session):
    """Verify valid user registration with password hashing."""
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": f"  {email.upper()}  ",  # Tests email normalization (trim and lowercase)
        "password": "SecurePassword123!",
        "display_name": "Test User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == email.lower()
    assert data["display_name"] == "Test User"
    assert data["is_active"] is True
    assert data["is_verified"] is False
    assert "id" in data
    # Security: password_hash and password must NEVER be in response
    assert "password" not in data
    assert "password_hash" not in data

    # Verify DB state: password is saved as an Argon2 hash, not plaintext
    user_db = db_session.execute(select(User).where(User.email == email.lower())).scalar_one()
    assert user_db.password_hash != "SecurePassword123!"
    assert "$argon2" in user_db.password_hash


def test_register_user_does_not_create_person(client, db_session):
    """CRITICAL ARCHITECTURE RULE: Registering a USER must NOT automatically create a PERSON."""
    initial_person_count = db_session.execute(select(func.count(Person.id))).scalar()

    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "ValidPassword123",
        "display_name": "Separate Identity",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    final_person_count = db_session.execute(select(func.count(Person.id))).scalar()
    assert final_person_count == initial_person_count, "Registration violated architecture: a Person record was created!"


def test_register_duplicate_email(client):
    """Verify duplicate email registration is rejected."""
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    payload = {"email": email, "password": "Password12345"}
    
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 409


def test_register_invalid_email(client):
    """Verify malformed email addresses are rejected."""
    payload = {"email": "not-an-email", "password": "ValidPassword123"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_empty_email(client):
    """Verify empty email is rejected."""
    payload = {"email": "", "password": "ValidPassword123"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_short_password(client):
    """Verify password shorter than 8 characters is rejected."""
    payload = {"email": f"short_{uuid.uuid4().hex[:6]}@example.com", "password": "short"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_long_password(client):
    """Verify password exceeding 128 characters is rejected."""
    payload = {"email": f"long_{uuid.uuid4().hex[:6]}@example.com", "password": "a" * 129}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_whitespace_password(client):
    """Verify whitespace-only password is rejected."""
    payload = {"email": f"space_{uuid.uuid4().hex[:6]}@example.com", "password": "        "}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


# ==============================================================================
# 2. LOGIN TESTS
# ==============================================================================

def test_login_success(client):
    """Verify login with correct credentials returns token pair."""
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = "CorrectPassword123!"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_login_wrong_password(client):
    """Verify login with incorrect password returns 401."""
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/v1/auth/register", json={"email": email, "password": "RealPassword123!"})

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "WrongPassword123!"})
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "password_hash" not in response.text


def test_login_unknown_email(client):
    """Verify login with nonexistent email returns 401 (generic message)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "SomePassword123!"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client, db_session):
    """Verify inactive user cannot log in."""
    email = f"inactive_{uuid.uuid4().hex[:8]}@example.com"
    password = "UserPassword123!"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    user_id = uuid.UUID(reg.json()["id"])

    # Deactivate user in database
    user = db_session.get(User, user_id)
    user.is_active = False
    db_session.commit()

    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 403


# ==============================================================================
# 3. JWT TOKEN VALIDATION TESTS
# ==============================================================================

def test_jwt_valid_access_token(client):
    """Verify /me endpoint with valid access token."""
    email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    password = "MyPassword123!"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_res.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "password_hash" not in data


def test_jwt_missing_token(client):
    """Verify protected endpoint rejects request with missing token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_jwt_malformed_token(client):
    """Verify protected endpoint rejects malformed token."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-jwt-token"})
    assert response.status_code == 401


def test_jwt_invalid_signature(client):
    """Verify token signed with wrong secret key is rejected."""
    payload = {
        "sub": str(uuid.uuid4()),
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    fake_token = jwt.encode(payload, "completely_wrong_secret_key_12345678", algorithm="HS256")
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {fake_token}"})
    assert response.status_code == 401


def test_jwt_expired_token(client, db_session):
    """Verify expired access token is rejected."""
    user = User(
        email=f"exp_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=get_password_hash("ValidPass123"),
    )
    db_session.add(user)
    db_session.commit()

    expired_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(seconds=-10),  # expired 10 seconds ago
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_jwt_refresh_token_rejected_as_access_token(client, db_session):
    """Verify a refresh token CANNOT be used to access protected endpoints (/me)."""
    user = User(
        email=f"cross_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=get_password_hash("ValidPass123"),
    )
    db_session.add(user)
    db_session.commit()

    refresh_token = create_refresh_token(subject=user.id)
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 401
    assert "expected access token" in response.json()["detail"].lower()


# ==============================================================================
# 4. REFRESH TOKEN TESTS
# ==============================================================================

def test_refresh_token_success(client):
    """Verify exchanging a valid refresh token for a new token pair."""
    email = f"ref_{uuid.uuid4().hex[:8]}@example.com"
    password = "ValidPassword123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh_token = login_res.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_access_token_rejected_as_refresh_token(client):
    """Verify an access token CANNOT be used on /auth/refresh endpoint."""
    email = f"acc_{uuid.uuid4().hex[:8]}@example.com"
    password = "ValidPassword123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_res.json()["access_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401
    assert "expected refresh token" in response.json()["detail"].lower()


def test_refresh_token_expired(client, db_session):
    """Verify expired refresh token is rejected."""
    user = User(
        email=f"refexp_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=get_password_hash("ValidPass123"),
    )
    db_session.add(user)
    db_session.commit()

    expired_refresh = create_refresh_token(
        subject=user.id,
        expires_delta=timedelta(seconds=-10),
    )
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": expired_refresh})
    assert response.status_code == 401


# ==============================================================================
# 5. LOGOUT & REVOCATION BEHAVIOR TESTS
# ==============================================================================

def test_logout_endpoint(client):
    """Verify logout endpoint responds with confirmation and advice to purge client tokens."""
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password12345"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access_token = login_res.json()["access_token"]

    response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["revoked"] is True
    assert "logged out" in data["message"].lower()


# ==============================================================================
# 6. SECURITY SENSITIVITY TESTS
# ==============================================================================

def test_no_sensitive_fields_exposed(client):
    """Verify that password hashes, JWT secrets, and database credentials are never leaked."""
    email = f"sec_{uuid.uuid4().hex[:8]}@example.com"
    password = "Password12345"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    for res in [reg, login, me]:
        body = res.text
        assert "password_hash" not in body
        assert settings.JWT_SECRET_KEY not in body
        if settings.DATABASE_URL:
            # Full raw connection string with password must never appear
            assert settings.DATABASE_URL not in body
