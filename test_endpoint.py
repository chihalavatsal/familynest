from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_user
from app.db.models.user import User
import uuid

# Mock current user
def override_get_current_user():
    user = User()
    user.id = uuid.UUID("d09f2280-e9f0-4336-8773-b3fff24af47d") # Extracted from logs
    return user

app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)
response = client.get("/api/v1/people/44cb6ff7-c06c-4c3f-a814-cabdad6b0186/timeline")
print("STATUS:", response.status_code)
print("BODY:", response.text)
