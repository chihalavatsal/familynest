import asyncio
from httpx import AsyncClient

async def test():
    # Login as one of the users
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post("/api/v1/auth/login", data={"username": "testfixture@example.com", "password": "password123"})
        if response.status_code != 200:
            print("Login failed", response.text)
            return
        token = response.json()["access_token"]
        
        resp = await ac.get("/api/v1/profile/dashboard", headers={"Authorization": f"Bearer {token}"})
        print(resp.status_code)
        print(resp.text[:500])

asyncio.run(test())
