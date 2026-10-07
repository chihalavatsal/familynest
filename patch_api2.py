import re
with open("backend/app/api/v1/api.py", "r") as f:
    content = f.read()

if "employments_router" not in content:
    content = content.replace("from app.api.v1.people import router as people_router", "from app.api.v1.people import router as people_router\nfrom app.api.v1.employments import router as employments_router")
    content = content.replace("api_router.include_router(people_router)", "api_router.include_router(people_router)\napi_router.include_router(employments_router)")

with open("backend/app/api/v1/api.py", "w") as f:
    f.write(content)
