with open("frontend/src/pages/Login/LoginPage.tsx", "r") as f:
    code = f.read()

code = code.replace("const navigate = useNavigate();", "const navigate = useNavigate();\n  const [searchParams] = useSearchParams();")

with open("frontend/src/pages/Login/LoginPage.tsx", "w") as f:
    f.write(code)
