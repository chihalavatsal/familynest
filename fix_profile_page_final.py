import re

with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

# Remove unused imports
content = content.replace("import { Input } from '../../components/ui/Input';\n", "")
content = content.replace("import { Select, Textarea } from '../../components/ui/FormFields';\n", "")

# Remove unused state
content = re.sub(r'\s*const \[editValues, setEditValues\].*?\n', '\n', content)
content = re.sub(r'\s*const \[isSaving, setIsSaving\].*?\n', '\n', content)
content = re.sub(r'\s*const \[saveError, setSaveError\].*?\n', '\n', content)

# Remove unused handleEditChange
content = re.sub(r'\s*const handleEditChange = \(field.*?\}\;\n', '\n', content, flags=re.DOTALL)

# Fix initialValues
content = content.replace("initialValues={profile?.person || {}}", "initialValues={profile || {}}")

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
