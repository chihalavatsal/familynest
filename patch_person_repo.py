import re
with open("backend/app/repositories/person_repository.py", "r") as f:
    content = f.read()

# We need to import FamilyMember
if "FamilyMember" not in content:
    content = content.replace("from app.db.models.person import Person", "from app.db.models.person import Person\nfrom app.db.models.family import FamilyMember")

old_query = """        stmt = select(Person).where(Person.created_by_user_id == user_id)"""

new_query = """        # Phase 20: Shared Family Network Access
        # A user can access a person if:
        # 1. They created it
        # 2. They claimed it
        # 3. They share a family network with it
        subq_my_person = select(Person.id).where(Person.claimed_by_user_id == user_id).scalar_subquery()
        subq_my_families = select(FamilyMember.family_id).where(FamilyMember.person_id == subq_my_person).scalar_subquery()
        subq_shared_people = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(subq_my_families)).scalar_subquery()

        stmt = select(Person).where(
            or_(
                Person.created_by_user_id == user_id,
                Person.claimed_by_user_id == user_id,
                Person.id.in_(subq_shared_people)
            )
        )"""

content = content.replace(old_query, new_query)

# Also fix the count query which currently does:
old_count = """        count_stmt = select(func.count()).select_from(Person).where(
            Person.created_by_user_id == user_id
        )"""

new_count = """        # Count also needs the same logic
        count_stmt = select(func.count()).select_from(Person).where(
            or_(
                Person.created_by_user_id == user_id,
                Person.claimed_by_user_id == user_id,
                Person.id.in_(subq_shared_people)
            )
        )"""
content = content.replace(old_count, new_count)

# Wait, we need to do this for get_by_id too!
old_get = """    def get_by_id(self, *, user_id: uuid.UUID, person_id: uuid.UUID) -> Optional[Person]:
        \"\"\"Retrieve a single Person by ID, ensuring the user owns it.\"\"\"
        stmt = select(Person).where(
            Person.id == person_id,
            Person.created_by_user_id == user_id
        )
        return self.db.execute(stmt).scalar_one_or_none()"""

new_get = """    def get_by_id(self, *, user_id: uuid.UUID, person_id: uuid.UUID) -> Optional[Person]:
        \"\"\"Retrieve a single Person by ID, ensuring the user has access.\"\"\"
        subq_my_person = select(Person.id).where(Person.claimed_by_user_id == user_id).scalar_subquery()
        subq_my_families = select(FamilyMember.family_id).where(FamilyMember.person_id == subq_my_person).scalar_subquery()
        subq_shared_people = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(subq_my_families)).scalar_subquery()

        stmt = select(Person).where(
            Person.id == person_id,
            or_(
                Person.created_by_user_id == user_id,
                Person.claimed_by_user_id == user_id,
                Person.id.in_(subq_shared_people)
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()"""
content = content.replace(old_get, new_get)

with open("backend/app/repositories/person_repository.py", "w") as f:
    f.write(content)
