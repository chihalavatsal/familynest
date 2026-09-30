"""Phase 3 — People Domain API Test Suite.

Tests:
  1.  Authentication guard — all endpoints require Bearer token
  2.  Create person — valid minimal payload
  3.  Create person — valid full payload
  4.  Create person — first_name required
  5.  Create person — first_name whitespace rejected
  6.  Create person — future date_of_birth rejected
  7.  Create person — future date_of_death rejected
  8.  Create person — death before birth rejected
  9.  Create person — invalid email rejected
  10. Create person — valid email normalised to lowercase
  11. Create person — created_by_user_id set from token (NOT client-controlled)
  12. Create person — claimed_by_user_id not exposed in create payload
  13. Create person — profile_status defaults to 'unclaimed'
  14. Create person — client may override profile_status to 'claimed'
  15. Create person — audit log written
  16. List people — authenticated user sees only their own persons
  17. List people — pagination (page, page_size, total)
  18. List people — search by first_name
  19. List people — search by last_name
  20. List people — search by nickname
  21. List people — invalid sort_by silently falls back to created_at
  22. List people — page_size capped at 100
  23. List people — empty result when no persons created
  24. Get person — creator can fetch own person
  25. Get person — 404 for non-existent id
  26. Get person — 404 for another user's person (privacy-preserving)
  27. Get person — phone and email present in detail response
  28. Patch person — partial update (single field)
  29. Patch person — multiple fields updated atomically
  30. Patch person — empty body returns 200 unchanged
  31. Patch person — 404 for non-existent person
  32. Patch person — 404 for another user's person
  33. Patch person — audit log written on update
  34. Patch person — cannot change claimed_by_user_id via patch
  35. Patch person — cannot change created_by_user_id via patch
  36. User/Person separation — creating a person does NOT affect auth tests
"""
import uuid
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.audit_log import AuditLog
from app.core.security import get_password_hash, create_access_token


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def db_session():
    """Transactional session that rolls back after each test (protects Neon data)."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient with db_session override — zero database pollution."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _make_user(db_session, *, email: str = None, display_name: str = "Test User") -> User:
    """Insert a User directly into the test session."""
    email = email or f"user_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        email=email,
        display_name=display_name,
        password_hash=get_password_hash("TestPassword123!"),
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    db_session.flush()
    return user


def _auth_headers(user: User) -> dict:
    """Return Authorization headers for a User."""
    token = create_access_token(subject=str(user.id))
    return {"Authorization": f"Bearer {token}"}


def _minimal_person_payload() -> dict:
    """Minimal valid PersonCreate payload."""
    return {"first_name": "Ramesh"}


def _full_person_payload() -> dict:
    """Full valid PersonCreate payload."""
    return {
        "first_name": "Ramesh",
        "middle_name": "Kumar",
        "last_name": "Patel",
        "nickname": "Ram",
        "gender": "male",
        "date_of_birth": "1970-06-15",
        "birth_place": "Mumbai, India",
        "current_city": "Bangalore",
        "occupation": "Engineer",
        "bio": "A senior engineer.",
        "phone": "+91-9876543210",
        "email": "ramesh.patel@example.com",
        "is_deceased": False,
        "is_minor": False,
        "profile_status": "unclaimed",
    }


# =============================================================================
# 1. Authentication Guard
# =============================================================================

class TestAuthenticationGuard:
    """All People endpoints must reject requests without a valid Bearer token."""

    def test_create_person_requires_auth(self, client):
        resp = client.post("/api/v1/people", json=_minimal_person_payload())
        assert resp.status_code == 401

    def test_list_people_requires_auth(self, client):
        resp = client.get("/api/v1/people")
        assert resp.status_code == 401

    def test_get_person_requires_auth(self, client):
        resp = client.get(f"/api/v1/people/{uuid.uuid4()}")
        assert resp.status_code == 401

    def test_patch_person_requires_auth(self, client):
        resp = client.patch(f"/api/v1/people/{uuid.uuid4()}", json={"first_name": "X"})
        assert resp.status_code == 401


# =============================================================================
# 2-15. Create Person
# =============================================================================

class TestCreatePerson:

    def test_create_minimal_payload(self, client, db_session):
        """Minimal payload (first_name only) should succeed with 201."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json=_minimal_person_payload(),
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["first_name"] == "Ramesh"
        assert "id" in data
        assert data["profile_status"] == "unclaimed"

    def test_create_full_payload(self, client, db_session):
        """Full payload should succeed and round-trip all provided fields."""
        user = _make_user(db_session)
        payload = _full_person_payload()
        resp = client.post(
            "/api/v1/people",
            json=payload,
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["first_name"] == "Ramesh"
        assert data["last_name"] == "Patel"
        assert data["email"] == "ramesh.patel@example.com"
        assert data["date_of_birth"] == "1970-06-15"

    def test_first_name_required(self, client, db_session):
        """Missing first_name must be rejected with 422."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"last_name": "Patel"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_first_name_whitespace_rejected(self, client, db_session):
        """Whitespace-only first_name must be rejected with 422."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "   "},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_future_date_of_birth_rejected(self, client, db_session):
        """date_of_birth in the future must be rejected with 422."""
        user = _make_user(db_session)
        future = (date.today() + timedelta(days=365)).isoformat()
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Future", "date_of_birth": future},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_future_date_of_death_rejected(self, client, db_session):
        """date_of_death in the future must be rejected with 422."""
        user = _make_user(db_session)
        future = (date.today() + timedelta(days=1)).isoformat()
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Future", "date_of_death": future},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_death_before_birth_rejected(self, client, db_session):
        """date_of_death before date_of_birth must be rejected with 422."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={
                "first_name": "Bad",
                "date_of_birth": "2000-01-01",
                "date_of_death": "1999-01-01",
            },
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_invalid_email_rejected(self, client, db_session):
        """Malformed email must be rejected with 422."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Bad", "email": "not-an-email"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 422

    def test_email_normalised_to_lowercase(self, client, db_session):
        """Email provided in mixed case must be stored and returned lowercased."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Ramesh", "email": "Ramesh.PATEL@Example.COM"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "ramesh.patel@example.com"

    def test_created_by_user_id_set_from_token(self, client, db_session):
        """created_by_user_id must equal the authenticated user's id."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json=_minimal_person_payload(),
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        assert resp.json()["created_by_user_id"] == str(user.id)

    def test_client_cannot_set_created_by_user_id(self, client, db_session):
        """Even if client sends created_by_user_id in body, it must be ignored."""
        user = _make_user(db_session)
        fake_id = str(uuid.uuid4())
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Ramesh", "created_by_user_id": fake_id},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        # Must equal real user's id, not the injected fake_id
        assert resp.json()["created_by_user_id"] == str(user.id)

    def test_profile_status_defaults_to_unclaimed(self, client, db_session):
        """profile_status must default to 'unclaimed' if not specified."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Ramesh"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        assert resp.json()["profile_status"] == "unclaimed"

    def test_client_can_set_profile_status(self, client, db_session):
        """Client may set profile_status to a valid value like 'invited'."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Ramesh", "profile_status": "invited"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        assert resp.json()["profile_status"] == "invited"

    def test_create_person_writes_audit_log(self, client, db_session):
        """Creating a Person must produce an audit_log entry with action='person.create'."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json=_minimal_person_payload(),
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        person_id = uuid.UUID(resp.json()["id"])

        audit = db_session.execute(
            select(AuditLog).where(
                AuditLog.action == "person.create",
                AuditLog.entity_type == "person",
                AuditLog.entity_id == person_id,
            )
        ).scalar_one_or_none()

        assert audit is not None
        assert audit.actor_user_id == user.id


# =============================================================================
# 16-23. List People
# =============================================================================

class TestListPeople:

    def _create_person(self, client, user, **overrides):
        payload = {**_minimal_person_payload(), **overrides}
        resp = client.post("/api/v1/people", json=payload, headers=_auth_headers(user))
        assert resp.status_code == 201
        return resp.json()

    def test_list_returns_only_own_persons(self, client, db_session):
        """A user must only see persons they created."""
        user_a = _make_user(db_session, email="a@example.com")
        user_b = _make_user(db_session, email="b@example.com")

        self._create_person(client, user_a, first_name="Alice")
        self._create_person(client, user_b, first_name="Bob")

        resp = client.get("/api/v1/people", headers=_auth_headers(user_a))
        assert resp.status_code == 200
        data = resp.json()
        names = [p["first_name"] for p in data["items"]]
        assert "Alice" in names
        assert "Bob" not in names

    def test_pagination_metadata(self, client, db_session):
        """Response must include correct page, page_size, and total fields."""
        user = _make_user(db_session)
        for i in range(3):
            self._create_person(client, user, first_name=f"Person{i}")

        resp = client.get(
            "/api/v1/people?page=1&page_size=2",
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["items"]) == 2
        assert data["total"] == 3

    def test_search_by_first_name(self, client, db_session):
        """?search= should match against first_name."""
        user = _make_user(db_session)
        self._create_person(client, user, first_name="Ramesh")
        self._create_person(client, user, first_name="Suresh")

        resp = client.get("/api/v1/people?search=Ramesh", headers=_auth_headers(user))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all("ramesh" in p["first_name"].lower() for p in items)
        assert len(items) == 1

    def test_search_by_last_name(self, client, db_session):
        """?search= should match against last_name."""
        user = _make_user(db_session)
        self._create_person(client, user, first_name="Alice", last_name="Sharma")
        self._create_person(client, user, first_name="Bob", last_name="Verma")

        resp = client.get("/api/v1/people?search=Sharma", headers=_auth_headers(user))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["last_name"] == "Sharma"

    def test_search_by_nickname(self, client, db_session):
        """?search= should match against nickname."""
        user = _make_user(db_session)
        self._create_person(client, user, first_name="Rajesh", nickname="Raju")
        self._create_person(client, user, first_name="Mahesh")

        resp = client.get("/api/v1/people?search=Raju", headers=_auth_headers(user))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) == 1
        assert items[0]["nickname"] == "Raju"

    def test_invalid_sort_by_falls_back(self, client, db_session):
        """An invalid sort_by must not raise 422 — silently falls back to created_at."""
        user = _make_user(db_session)
        self._create_person(client, user)

        resp = client.get(
            "/api/v1/people?sort_by=INVALID_COLUMN",
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200

    def test_page_size_capped_at_100(self, client, db_session):
        """page_size > 100 must be rejected at the query param validation level."""
        user = _make_user(db_session)
        resp = client.get("/api/v1/people?page_size=999", headers=_auth_headers(user))
        assert resp.status_code == 422

    def test_empty_list_when_no_persons(self, client, db_session):
        """User with no created persons must receive empty list with total=0."""
        user = _make_user(db_session)
        resp = client.get("/api/v1/people", headers=_auth_headers(user))
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_excludes_phone_and_email(self, client, db_session):
        """phone and email must NOT appear in list response items."""
        user = _make_user(db_session)
        self._create_person(
            client, user,
            first_name="Ramesh",
            phone="+91-9876543210",
            email="ramesh@example.com",
        )
        resp = client.get("/api/v1/people", headers=_auth_headers(user))
        assert resp.status_code == 200
        item = resp.json()["items"][0]
        assert "phone" not in item
        assert "email" not in item


# =============================================================================
# 24-27. Get Person Detail
# =============================================================================

class TestGetPerson:

    def _create_person(self, client, user, **overrides):
        payload = {**_minimal_person_payload(), **overrides}
        resp = client.post("/api/v1/people", json=payload, headers=_auth_headers(user))
        assert resp.status_code == 201
        return resp.json()

    def test_creator_can_get_own_person(self, client, db_session):
        """Creator should receive 200 with full person detail."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="Ramesh")
        person_id = created["id"]

        resp = client.get(f"/api/v1/people/{person_id}", headers=_auth_headers(user))
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == person_id
        assert data["first_name"] == "Ramesh"

    def test_get_nonexistent_person_returns_404(self, client, db_session):
        """GET with a random UUID that does not exist must return 404."""
        user = _make_user(db_session)
        resp = client.get(
            f"/api/v1/people/{uuid.uuid4()}",
            headers=_auth_headers(user),
        )
        assert resp.status_code == 404

    def test_get_other_users_person_returns_404(self, client, db_session):
        """Privacy-preserving: another user's person must return 404 (not 403)."""
        user_a = _make_user(db_session, email="a2@example.com")
        user_b = _make_user(db_session, email="b2@example.com")

        created = self._create_person(client, user_a, first_name="Private")
        person_id = created["id"]

        resp = client.get(
            f"/api/v1/people/{person_id}",
            headers=_auth_headers(user_b),
        )
        assert resp.status_code == 404

    def test_detail_includes_phone_and_email(self, client, db_session):
        """GET detail must include phone and email (unlike list)."""
        user = _make_user(db_session)
        created = self._create_person(
            client, user,
            first_name="Contact",
            phone="+91-9876543210",
            email="contact@example.com",
        )
        person_id = created["id"]

        resp = client.get(f"/api/v1/people/{person_id}", headers=_auth_headers(user))
        assert resp.status_code == 200
        data = resp.json()
        assert data["phone"] == "+91-9876543210"
        assert data["email"] == "contact@example.com"


# =============================================================================
# 28-35. Patch Person
# =============================================================================

class TestPatchPerson:

    def _create_person(self, client, user, **overrides):
        payload = {**_minimal_person_payload(), **overrides}
        resp = client.post("/api/v1/people", json=payload, headers=_auth_headers(user))
        assert resp.status_code == 201
        return resp.json()

    def test_patch_single_field(self, client, db_session):
        """Patching a single field must update only that field."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="OldName")
        person_id = created["id"]

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"first_name": "NewName"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "NewName"

    def test_patch_multiple_fields(self, client, db_session):
        """Patching multiple fields must update all provided fields atomically."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="Ramesh")
        person_id = created["id"]

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"last_name": "Patel", "occupation": "Doctor", "nickname": "Ram"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["last_name"] == "Patel"
        assert data["occupation"] == "Doctor"
        assert data["nickname"] == "Ram"

    def test_patch_empty_body_returns_200(self, client, db_session):
        """PATCH with empty JSON body must return 200 without modifying the record."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="Stable")
        person_id = created["id"]

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Stable"

    def test_patch_nonexistent_person_returns_404(self, client, db_session):
        """PATCH on a non-existent UUID must return 404."""
        user = _make_user(db_session)
        resp = client.patch(
            f"/api/v1/people/{uuid.uuid4()}",
            json={"first_name": "Ghost"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 404

    def test_patch_other_users_person_returns_404(self, client, db_session):
        """Privacy-preserving: patching another user's person must return 404."""
        user_a = _make_user(db_session, email="pa@example.com")
        user_b = _make_user(db_session, email="pb@example.com")

        created = self._create_person(client, user_a, first_name="Alice")
        person_id = created["id"]

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"first_name": "Hacked"},
            headers=_auth_headers(user_b),
        )
        assert resp.status_code == 404

    def test_patch_writes_audit_log(self, client, db_session):
        """Updating a Person must produce an audit_log entry with action='person.update'."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="ToUpdate")
        person_id = uuid.UUID(created["id"])

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"occupation": "Surgeon"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 200

        audit = db_session.execute(
            select(AuditLog).where(
                AuditLog.action == "person.update",
                AuditLog.entity_type == "person",
                AuditLog.entity_id == person_id,
            )
        ).scalar_one_or_none()

        assert audit is not None
        assert audit.actor_user_id == user.id

    def test_patch_cannot_set_claimed_by_user_id(self, client, db_session):
        """claimed_by_user_id must be ignored if provided in patch payload."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="Ramesh")
        person_id = created["id"]

        # claimed_by_user_id is not in PersonUpdate schema — FastAPI should ignore or 422
        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"claimed_by_user_id": str(uuid.uuid4())},
            headers=_auth_headers(user),
        )
        # Either 200 (field ignored by Pydantic) or 422 (field not in schema)
        # Either way, claimed_by_user_id in DB must NOT have changed
        assert resp.status_code in (200, 422)
        if resp.status_code == 200:
            assert resp.json()["claimed_by_user_id"] is None

    def test_patch_cannot_set_created_by_user_id(self, client, db_session):
        """created_by_user_id must be ignored if provided in patch payload."""
        user = _make_user(db_session)
        created = self._create_person(client, user, first_name="Ramesh")
        person_id = created["id"]
        original_creator = created["created_by_user_id"]

        resp = client.patch(
            f"/api/v1/people/{person_id}",
            json={"created_by_user_id": str(uuid.uuid4())},
            headers=_auth_headers(user),
        )
        assert resp.status_code in (200, 422)
        if resp.status_code == 200:
            assert resp.json()["created_by_user_id"] == original_creator


# =============================================================================
# 36. User/Person Separation
# =============================================================================

class TestUserPersonSeparation:

    def test_create_person_does_not_create_user(self, client, db_session):
        """Creating a Person must NOT create an additional User record."""
        from sqlalchemy import func, select
        user = _make_user(db_session)

        user_count_before = db_session.execute(
            select(func.count()).select_from(User)
        ).scalar_one()

        client.post(
            "/api/v1/people",
            json={"first_name": "Ramesh"},
            headers=_auth_headers(user),
        )

        user_count_after = db_session.execute(
            select(func.count()).select_from(User)
        ).scalar_one()

        assert user_count_after == user_count_before

    def test_person_exists_without_user_account(self, client, db_session):
        """A created Person must have profile_status 'unclaimed' and no claimed_by_user_id."""
        user = _make_user(db_session)
        resp = client.post(
            "/api/v1/people",
            json={"first_name": "Unclaimed"},
            headers=_auth_headers(user),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_status"] == "unclaimed"
        assert data["claimed_by_user_id"] is None
