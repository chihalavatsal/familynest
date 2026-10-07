import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, SessionLocal, engine
from app.db.models.user import User

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(email="testfixture@example.com", display_name="Fixture User")
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash("password123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def normal_user_token_headers(test_user):
    from app.core.security import create_access_token
    token = create_access_token(subject=test_user.id)
    return {"Authorization": f"Bearer {token}"}
