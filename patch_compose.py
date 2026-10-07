import os

f = "docker-compose.yml"
with open(f, "r") as file:
    content = file.read()

content = content.replace(
    "- SECRET_KEY=${SECRET_KEY}",
    "- SECRET_KEY=${SECRET_KEY}\n      - JWT_SECRET_KEY=${JWT_SECRET_KEY}"
)

with open(f, "w") as file:
    file.write(content)
print("Done")
