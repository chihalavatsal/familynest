import psycopg
import os
import httpx

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        from app.core.config import settings
        from app.core.security import create_access_token
        from datetime import timedelta
        token = create_access_token(subject=str('d09f2280-e9f0-4336-8773-b3fff24af47d'), expires_delta=timedelta(minutes=15))
        
        headers = {"Authorization": f"Bearer {token}"}
        res = httpx.get("http://127.0.0.1:8000/api/v1/events?limit=100", headers=headers)
        print("GET /events:", res.json())
