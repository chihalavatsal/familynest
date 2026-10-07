import re
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

if "AddRelativeWizard" not in content:
    content = content.replace("import { PersonForm } from '../../components/people/PersonForm';", "import { PersonForm } from '../../components/people/PersonForm';\nimport { AddRelativeWizard } from '../../components/people/AddRelativeWizard';")

old_modal = r'<PersonForm\s+isCreate[\s\S]*?onCancel=\{.*?\}\s+/>'
new_modal = """<AddRelativeWizard 
          currentPersonId={undefined}
          preselectedFamilyId={familyId}
          onComplete={() => {
            setShowAddMember(false);
            loadFamily();
          }}
          onCancel={() => setShowAddMember(false)}
        />"""

content = re.sub(old_modal, new_modal, content)

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
