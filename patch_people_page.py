import re
with open("frontend/src/pages/People/PeoplePage.tsx", "r") as f:
    content = f.read()

if "AddRelativeWizard" not in content:
    content = content.replace("import { PersonForm } from '../../components/people/PersonForm';", "import { PersonForm } from '../../components/people/PersonForm';\nimport { AddRelativeWizard } from '../../components/people/AddRelativeWizard';")

old_modal = r'<PersonForm\s+isCreate[\s\S]*?onCancel=\{.*?\}\s+/>'
new_modal = """<AddRelativeWizard 
          currentPersonId={profile?.person?.id}
          onComplete={() => {
            setShowCreate(false);
            loadPeople();
            success('Person added successfully.');
          }}
          onCancel={() => setShowCreate(false)}
        />"""

content = re.sub(old_modal, new_modal, content)

with open("frontend/src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(content)
