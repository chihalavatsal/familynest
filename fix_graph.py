import re

with open('backend/app/schemas/relationship_graph.py', 'r') as f:
    code = f.read()

# Delete the redefined class SafePersonSummary
class_def_start = code.find("class SafePersonSummary(BaseModel):")
if class_def_start != -1:
    class_def_end = code.find("\n\nclass RelationshipPathNode", class_def_start)
    if class_def_end != -1:
        code = code[:class_def_start] + code[class_def_end+2:]

with open('backend/app/schemas/relationship_graph.py', 'w') as f:
    f.write(code)
