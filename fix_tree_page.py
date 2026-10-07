import re
with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    content = f.read()

content = content.replace("import { PersonForm } from '../../components/people/PersonForm';\n", "")

old_modal = r'<PersonForm\s+isCreate\s+currentPersonId=\{centerPerson\?\.id\}[\s\S]*?onCancel=\{.*?\}\s+/>'
new_modal = """<AddRelativeWizard 
          currentPersonId={centerPerson?.id}
          onComplete={() => {
            setShowAddRelative(false);
            loadGraph();
            success('Relative added successfully.');
          }}
          onCancel={() => setShowAddRelative(false)}
        />"""

content = re.sub(old_modal, new_modal, content)

# Remove handleAddRelative since it's unused now
content = re.sub(r'\s*const handleAddRelative = async \(values: any\) => \{.*?\n  \};\n', '\n', content, flags=re.DOTALL)

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(content)
