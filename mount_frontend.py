import re

with open("backend/app/main.py", "r") as f:
    code = f.read()

# Add FastAPI StaticFiles mount if not exists
mount_code = """
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount production React frontend
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Ignore API routes
        if full_path.startswith("api/"):
            return None
            
        # Serve specific files if they exist
        path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(path):
            return FileResponse(path)
            
        # SPA fallback to index.html
        return FileResponse(os.path.join(frontend_dist, "index.html"))
"""

if "frontend_dist =" not in code:
    code = code.replace('app.include_router(api_router, prefix="/api/v1")', 'app.include_router(api_router, prefix="/api/v1")\n' + mount_code)
    with open("backend/app/main.py", "w") as f:
        f.write(code)
