import os

f = "docker-compose.yml"
with open(f, "r") as file:
    content = file.read()

content = content.replace(
    "- JWT_SECRET_KEY=${JWT_SECRET_KEY}",
    "- JWT_SECRET_KEY=${JWT_SECRET_KEY}\n      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}"
)

with open(f, "w") as file:
    file.write(content)
print("Done")
