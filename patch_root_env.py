import os

f = ".env"
with open(f, "r") as file:
    content = file.read()

content = content.replace(
    'BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://127.0.0.1:5173"]',
    'BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:3000","http://127.0.0.1:5173"]'
)

with open(f, "w") as file:
    file.write(content)
print("Done")
