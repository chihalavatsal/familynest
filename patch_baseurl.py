with open("frontend/src/api/client.ts", "r") as f:
    code = f.read()

code = code.replace("'http://localhost:8000/api/v1'", "'http://127.0.0.1:8000/api/v1'")

with open("frontend/src/api/client.ts", "w") as f:
    f.write(code)
