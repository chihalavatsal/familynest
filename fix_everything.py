import re

# 1. Fix relationship_graph.py
with open('backend/app/schemas/relationship_graph.py', 'r') as f:
    code = f.read()

code = code.replace("from app.schemas.person import SafePersonSummary", "from app.schemas.person import PersonListItem")
code = code.replace("SafePersonSummary", "PersonListItem")
with open('backend/app/schemas/relationship_graph.py', 'w') as f:
    f.write(code)

# 2. Fix relationship_graph_service.py
with open('backend/app/services/relationship_graph_service.py', 'r') as f:
    code = f.read()
code = code.replace("from app.schemas.person import SafePersonSummary", "")
code = code.replace("SafePersonSummary", "PersonListItem")
# Need to import PersonListItem in service
if "from app.schemas.person import PersonListItem" not in code:
    code = "from app.schemas.person import PersonListItem\n" + code

with open('backend/app/services/relationship_graph_service.py', 'w') as f:
    f.write(code)

# 3. Fix invitation.py and person_claim_service.py to point back to person.py for PersonListItem
def fix_import(filename):
    with open(filename, 'r') as f:
        content = f.read()
    content = content.replace("from app.schemas.relationship_graph import PersonListItem", "from app.schemas.person import PersonListItem")
    with open(filename, 'w') as f:
        f.write(content)

fix_import('backend/app/schemas/invitation.py')
fix_import('backend/app/services/person_claim_service.py')

