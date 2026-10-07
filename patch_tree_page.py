import re
with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    content = f.read()

if "AddRelativeWizard" not in content:
    content = content.replace("import { PersonForm } from '../../components/people/PersonForm';", "import { PersonForm } from '../../components/people/PersonForm';\nimport { AddRelativeWizard } from '../../components/people/AddRelativeWizard';")

# Let's find where PersonForm is used for Add Relative
old_modal = r'<PersonForm\s+isCreate\s+currentPersonId=\{centerPerson\.id\}[\s\S]*?onCancel=\{.*?\}\s+/>'
new_modal = """<AddRelativeWizard 
          currentPersonId={centerPerson.id}
          onComplete={() => {
            setShowAddPerson(false);
            loadGraph();
            success('Relative added successfully.');
          }}
          onCancel={() => setShowAddPerson(false)}
        />"""

content = re.sub(old_modal, new_modal, content)

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(content)
