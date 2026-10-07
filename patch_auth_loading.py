import re
with open("frontend/src/store/AuthContext.tsx", "r") as f:
    code = f.read()

# Remove dispatch({ type: 'AUTH_LOADING' }) from login and register
code = code.replace("dispatch({ type: 'AUTH_LOADING' });", "")

with open("frontend/src/store/AuthContext.tsx", "w") as f:
    f.write(code)
