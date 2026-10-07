with open("backend/app/repositories/family_repository.py", "r") as f:
    content = f.read()

bulk_count = """
    def count_members_bulk(self, family_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        from sqlalchemy import func
        stmt = select(FamilyMember.family_id, func.count(FamilyMember.person_id)).where(FamilyMember.family_id.in_(family_ids)).group_by(FamilyMember.family_id)
        result = self.db.execute(stmt).all()
        return {fam_id: count for fam_id, count in result}
"""
content += bulk_count
with open("backend/app/repositories/family_repository.py", "w") as f:
    f.write(content)

with open("backend/app/services/family_service.py", "r") as f:
    content = f.read()

loop_old = """        items = []
        for family in families:
            count = self.repo.count_members(family.id)
            items.append(_build_family_list_item(family, count))"""

loop_new = """        items = []
        counts = self.repo.count_members_bulk([f.id for f in families])
        for family in families:
            count = counts.get(family.id, 0)
            items.append(_build_family_list_item(family, count))"""

content = content.replace(loop_old, loop_new)
with open("backend/app/services/family_service.py", "w") as f:
    f.write(content)
