import os

f = "backend/app/api/v1/families.py"
with open(f, "r") as file:
    content = file.read()

if "from fastapi import APIRouter, Depends, HTTPException" not in content:
    content = content.replace(
        "from fastapi import APIRouter, Depends",
        "from fastapi import APIRouter, Depends, HTTPException"
    )

with open(f, "w") as file:
    file.write(content)
print("Done")
