import os
import re

with open('backend/app/schemas/relationship_graph.py', 'r') as f:
    code = f.read()

# Replace PersonListItem with SafePersonSummary in imports and usage
code = code.replace("class PersonListItem(BaseModel):", "from app.schemas.person import SafePersonSummary\n\nclass PersonListItem(BaseModel):")
code = code.replace("PersonListItem", "SafePersonSummary")

with open('backend/app/schemas/relationship_graph.py', 'w') as f:
    f.write(code)

with open('backend/app/services/relationship_graph_service.py', 'r') as f:
    code2 = f.read()

# Update _build_person_summary to use SafePersonSummary
old_def = """    def _build_person_summary(self, person_id: uuid.UUID) -> PersonListItem:
        p = self._people_cache[person_id]
        return PersonListItem(id=p.id, first_name=p.first_name, last_name=p.last_name)"""
        
new_def = """    def _build_person_summary(self, person_id: uuid.UUID) -> SafePersonSummary:
        p = self._people_cache[person_id]
        return SafePersonSummary.model_validate(p)"""

code2 = code2.replace(old_def, new_def)
code2 = code2.replace("from app.schemas.relationship_graph import ", "from app.schemas.relationship_graph import ")
code2 = code2.replace("PersonListItem", "SafePersonSummary")
# Also need to import SafePersonSummary
code2 = "from app.schemas.person import SafePersonSummary\n" + code2

with open('backend/app/services/relationship_graph_service.py', 'w') as f:
    f.write(code2)
