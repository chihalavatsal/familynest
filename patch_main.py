with open('backend/app/main.py', 'r') as f:
    code = f.read()

if "from fastapi import Request" not in code:
    code = code.replace("from fastapi import FastAPI", "from fastapi import FastAPI, Request")

with open('backend/app/main.py', 'w') as f:
    f.write(code)
