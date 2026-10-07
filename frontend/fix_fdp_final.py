with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

import re

# Add useAuth back if missing
if "import { useAuth }" not in content:
    content = content.replace("import { useToast } from '../../components/ui/Toast';", "import { useToast } from '../../components/ui/Toast';\nimport { useAuth } from '../../store/AuthContext';")

# Replace load() correctly
content = content.replace("initialize();", "load();")

# Remove extra profile var issues
# We must get profile from useAuth inside the component
if "const { profile } = useAuth" not in content:
    content = content.replace("const { success } = useToast();", "const { success } = useToast();\n  const { profile } = useAuth() as any;")

with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)

with open("src/pages/People/PeoplePage.tsx", "r") as f:
    pp = f.read()
pp = pp.replace("const { user, profile } = useAuth() as any;", "const { profile } = useAuth() as any;")
with open("src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(pp)
