import os

with open('backend/app/main.py', 'r') as f:
    code = f.read()

import re
code = re.sub(
    r'@app\.exception_handler\(Exception\).*?return JSONResponse\([^)]+\)',
    '',
    code,
    flags=re.DOTALL
)
# Also remove the imports
code = code.replace("from fastapi.responses import JSONResponse", "")
code = code.replace("import traceback", "")
code = code.replace("from fastapi import Request", "")

with open('backend/app/main.py', 'w') as f:
    f.write(code)
