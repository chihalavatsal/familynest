import re

authz_patch = """
    def can_read_person(self, user_id: uuid.UUID, person_id: uuid.UUID) -> bool:
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        
        # 1. Created by you or claimed by you
        person = self.db.execute(select(Person).where(Person.id == person_id)).scalar_one_or_none()
        if not person:
            return False
        if person.created_by_user_id == user_id or person.claimed_by_user_id == user_id:
            return True
            
        # 2. In a shared family
        # Find families the user is in
        user_fams = select(FamilyMember.family_id).where(FamilyMember.person_id.in_(
            select(Person.id).where(Person.claimed_by_user_id == user_id)
        ))
        
        # Check if person is in any of those families
        shared_fam = self.db.execute(
            select(FamilyMember).where(
                FamilyMember.person_id == person_id,
                FamilyMember.family_id.in_(user_fams)
            )
        ).first()
        
        if shared_fam:
            return True
            
        # Add fallback: what if user has not claimed a person but created the family?
        # A user in family is technically based on person_id in family.
        # So we just rely on that. If they are the creator of the person, we already caught it.
        
        return False

    def can_edit_person(self, user_id: uuid.UUID, person_id: uuid.UUID) -> bool:
        from app.db.models.person import Person
        person = self.db.execute(select(Person).where(Person.id == person_id)).scalar_one_or_none()
        if not person:
            return False
        # Claimed users can edit themselves
        if person.claimed_by_user_id == user_id:
            return True
        # Creators can edit unclaimed people they created
        if person.created_by_user_id == user_id and not person.claimed_by_user_id:
            return True
        return False

    def get_accessible_people(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        
        # People created or claimed by user
        q1 = select(Person.id).where((Person.created_by_user_id == user_id) | (Person.claimed_by_user_id == user_id))
        
        # People in shared families
        user_fams = select(FamilyMember.family_id).where(FamilyMember.person_id.in_(
            select(Person.id).where(Person.claimed_by_user_id == user_id)
        ))
        q2 = select(FamilyMember.person_id).where(FamilyMember.family_id.in_(user_fams))
        
        ids1 = self.db.execute(q1).scalars().all()
        ids2 = self.db.execute(q2).scalars().all()
        
        return list(set(list(ids1) + list(ids2)))
"""

with open("backend/app/services/authz_service.py", "r") as f:
    content = f.read()

# Add methods to the end of the class
if "def can_read_person" not in content:
    content += authz_patch

with open("backend/app/services/authz_service.py", "w") as f:
    f.write(content)
