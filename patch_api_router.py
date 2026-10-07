import re

with open('backend/app/api/v1/api.py', 'r') as f:
    content = f.read()

# Add import
content = content.replace(
    'from app.api.v1.search import router as search_router',
    'from app.api.v1.search import router as search_router\nfrom app.api.v1.timeline import router as timeline_router'
)

# Add route
content = content.replace(
    'api_router.include_router(search_router)',
    'api_router.include_router(search_router)\napi_router.include_router(timeline_router)'
)

with open('backend/app/api/v1/api.py', 'w') as f:
    f.write(content)
