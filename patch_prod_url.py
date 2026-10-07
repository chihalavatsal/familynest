with open("frontend/src/api/client.ts", "r") as f:
    code = f.read()

# Change the local IP to the real production Render API!
code = code.replace("'http://127.0.0.1:8000/api/v1'", "'https://familynest-uwxe.onrender.com/api/v1'")

with open("frontend/src/api/client.ts", "w") as f:
    f.write(code)
