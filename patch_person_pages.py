import re

# PersonDetailPage
with open("frontend/src/pages/People/PersonDetailPage.tsx", "r") as f:
    content = f.read()

if "EmploymentList" not in content:
    content = content.replace("import { PersonForm } from '../../components/people/PersonForm';", "import { PersonForm } from '../../components/people/PersonForm';\nimport { EmploymentList } from '../../components/people/EmploymentList';")
    content = content.replace("{/* About Section */}", "<EmploymentList personId={person.id} canEdit={canEdit} />\n            {/* About Section */}")

with open("frontend/src/pages/People/PersonDetailPage.tsx", "w") as f:
    f.write(content)

# ProfilePage
with open("frontend/src/pages/Profile/ProfilePage.tsx", "r") as f:
    content = f.read()

if "EmploymentList" not in content:
    content = content.replace("import { PersonForm } from '../../components/people/PersonForm';", "import { PersonForm } from '../../components/people/PersonForm';\nimport { EmploymentList } from '../../components/people/EmploymentList';")
    content = content.replace("{/* Personal Info */}", "<EmploymentList personId={profile.id} canEdit={true} />\n          {/* Personal Info */}")

with open("frontend/src/pages/Profile/ProfilePage.tsx", "w") as f:
    f.write(content)
