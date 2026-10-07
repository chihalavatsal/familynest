import re
with open("backend/app/main.py", "r") as f:
    code = f.read()

timing_middleware = """
import time
from starlette.requests import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"PATH: {request.url.path} TOOK: {process_time:.4f} seconds")
    return response
"""

if "add_process_time_header" not in code:
    code = code.replace('app = FastAPI(', timing_middleware + '\napp = FastAPI(')
    with open("backend/app/main.py", "w") as f:
        f.write(code)
