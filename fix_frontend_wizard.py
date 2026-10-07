import re

# Fix AddRelativeWizard
with open("frontend/src/components/people/AddRelativeWizard.tsx", "r") as f:
    content = f.read()
content = content.replace("import React, { useState, useEffect }", "import { useState, useEffect }")
content = content.replace("import { Select, Textarea } from '../ui/FormFields';", "import { Select } from '../ui/FormFields';")
content = content.replace("SafePersonSummary", "")
content = content.replace("q: searchQuery", "search: searchQuery")
with open("frontend/src/components/people/AddRelativeWizard.tsx", "w") as f:
    f.write(content)

# Fix FamilyDetailPage
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()
content = content.replace("import { PersonForm } from '../../components/people/PersonForm';\n", "")
content = re.sub(r'\s*const handleCreatePerson = async \(values: any\) => \{.*?\n  \};\n', '\n', content, flags=re.DOTALL)
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)

# Fix PeoplePage
with open("frontend/src/pages/People/PeoplePage.tsx", "r") as f:
    content = f.read()
content = content.replace("import { PersonForm } from '../../components/people/PersonForm';\n", "")
content = re.sub(r'\s*const handleCreate = async \(values: any\) => \{.*?\n  \};\n', '\n', content, flags=re.DOTALL)
content = content.replace("loadPeople();", "load();")
with open("frontend/src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(content)

# Fix FamilyTreePage
with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    content = f.read()
# Wait, why was AddRelativeWizard unused in FamilyTreePage? Let's check how many PersonForms there are.
# If I missed one, let's fix it.
