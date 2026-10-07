import re
with open("backend/app/tests/test_phase21_e2e.py", "r") as f:
    content = f.read()

content = content.replace(
    'rel_svc.create_relationship(user_a.id, person_a.id, brother.id, "sibling", is_current=True)',
    'from app.schemas.relationship import RelationshipCreate\n    rel_svc.create_relationship(user_a.id, RelationshipCreate(person_a_id=person_a.id, person_b_id=brother.id, relationship_type="sibling", is_current=True))'
)
content = content.replace(
    'rel_svc.create_relationship(user_b.id, brother.id, brother_wife.id, "spouse", is_current=True)',
    'rel_svc.create_relationship(user_b.id, RelationshipCreate(person_a_id=brother.id, person_b_id=brother_wife.id, relationship_type="spouse", is_current=True))'
)
with open("backend/app/tests/test_phase21_e2e.py", "w") as f:
    f.write(content)
