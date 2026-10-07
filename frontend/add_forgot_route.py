import re

with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace("import { AuthCallbackPage } from './pages/Login/AuthCallbackPage';", "import { AuthCallbackPage } from './pages/Login/AuthCallbackPage';\nimport { ForgotPasswordPage } from './pages/Login/ForgotPasswordPage';")

content = content.replace("<Route path=\"/login\" element={<LoginPage />} />", "<Route path=\"/login\" element={<LoginPage />} />\n              <Route path=\"/forgot-password\" element={<ForgotPasswordPage />} />")

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
