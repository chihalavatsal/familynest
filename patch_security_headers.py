with open("backend/app/main.py", "r") as f:
    content = f.read()

headers_middleware = """
from fastapi import Request

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'"
    return response

# Include API v1 Router
"""

content = content.replace("# Include API v1 Router", headers_middleware)
with open("backend/app/main.py", "w") as f:
    f.write(content)
