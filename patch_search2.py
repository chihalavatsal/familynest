with open("backend/app/services/search_service.py", "r") as f:
    content = f.read()

old_func = """    def _get_user_families(self, user_id: uuid.UUID):
        stmt = select(Family.id, Family.name).join(FamilyMember, FamilyMember.family_id == Family.id).where(FamilyMember.user_id == user_id)
        return {f.id: f.name for f in self.db.execute(stmt).all()}"""

new_func = """    def _get_user_families(self, user_id: uuid.UUID):
        stmt = select(Family.id, Family.name).join(FamilyMember, FamilyMember.family_id == Family.id).join(Person, Person.id == FamilyMember.person_id).where(Person.claimed_by_user_id == user_id)
        return {f.id: f.name for f in self.db.execute(stmt).all()}"""

content = content.replace(old_func, new_func)

with open("backend/app/services/search_service.py", "w") as f:
    f.write(content)
