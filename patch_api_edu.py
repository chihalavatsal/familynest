import re
with open("backend/app/api/v1/api.py", "r") as f:
    content = f.read()

if "educations_router" not in content:
    content = content.replace("from app.api.v1.employments import router as employments_router", "from app.api.v1.employments import router as employments_router\nfrom app.api.v1.educations import router as educations_router")
    content = content.replace("api_router.include_router(employments_router)", "api_router.include_router(employments_router)\napi_router.include_router(educations_router)")

with open("backend/app/api/v1/api.py", "w") as f:
    f.write(content)
