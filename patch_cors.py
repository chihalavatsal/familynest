import os

f = "backend/app/core/config.py"
with open(f, "r") as file:
    content = file.read()

content = content.replace(
    '"http://localhost:5173",',
    '"http://localhost:5173",\n        "http://localhost:5174",'
)

with open(f, "w") as file:
    file.write(content)
print("Done")
