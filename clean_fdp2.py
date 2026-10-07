import re
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

rel_block = """    if (values.relationship_type && myPersonId) {
      await relationshipsApi.create({
        person_a_id: myPersonId,
        person_b_id: person.id,
        relationship_type: values.relationship_type as any,
        is_current: true
      });
    }"""
content = content.replace(rel_block, "")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
