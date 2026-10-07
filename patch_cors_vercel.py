with open("backend/app/core/config.py", "r") as f:
    code = f.read()

import re
code = code.replace(
    '"http://127.0.0.1:5173",',
    '"http://127.0.0.1:5173",\n        "https://familynest-kappa.vercel.app",'
)

with open("backend/app/core/config.py", "w") as f:
    f.write(code)
