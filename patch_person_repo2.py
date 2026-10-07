import re
with open("backend/app/repositories/person_repository.py", "r") as f:
    content = f.read()

old_base_filter = "        # Base filter: creator-only access\n        base_filter = Person.created_by_user_id == user_id"

new_base_filter = """        # Base filter: Shared Family Network Access
        subq_my_person = select(Person.id).where(Person.claimed_by_user_id == user_id).scalar_subquery()
        subq_my_families = select(FamilyMember.family_id).where(FamilyMember.person_id == subq_my_person).scalar_subquery()
        subq_shared_people = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(subq_my_families)).scalar_subquery()

        base_filter = or_(
            Person.created_by_user_id == user_id,
            Person.claimed_by_user_id == user_id,
            Person.id.in_(subq_shared_people)
        )"""

content = content.replace(old_base_filter, new_base_filter)

with open("backend/app/repositories/person_repository.py", "w") as f:
    f.write(content)
