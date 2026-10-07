import re

with open('frontend/src/components/people/AddRelativeWizard.tsx', 'r') as f:
    content = f.read()

replacement = """      case 'father':
      case 'mother':
        return [{ person_a_id: targetPersonId, person_b_id: currentPersonId, relationship_type: 'parent' }];
      case 'son':
      case 'daughter':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'parent' }];
      case 'spouse':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'spouse' }];
      case 'brother':
      case 'sister':
        return [{ person_a_id: currentPersonId, person_b_id: targetPersonId, relationship_type: 'sibling' }];
      case 'guardian':
        return [{ person_a_id: targetPersonId, person_b_id: currentPersonId, relationship_type: 'guardian' }];

      // Extended relationships: create graph path through intermediate person"""

# We need to replace the buggy block.
pattern = re.compile(r"      case 'father':.*?// Extended relationships: create graph path through intermediate person", re.DOTALL)
content = pattern.sub(replacement, content)

with open('frontend/src/components/people/AddRelativeWizard.tsx', 'w') as f:
    f.write(content)
