import uuid
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.relationship import Relationship
from app.db.models.family import Family, FamilyMember


db = SessionLocal()

try:
    # 1. Get user
    user = db.query(User).filter_by(email="vatsalchihala@gmail.com").first()
    if not user:
        print("User not found")
        exit(1)

    # 2. Get Vatsal's person profile
    vatsal = db.query(Person).filter_by(claimed_by_user_id=user.id).first()
    if not vatsal:
        print("Vatsal person not found")
        exit(1)

    # 3. Delete everything EXCEPT Vatsal
    print("Deleting old records...")
    db.query(Relationship).delete()
    db.query(FamilyMember).delete()
    db.query(Family).delete()
    db.query(Person).filter(Person.id != vatsal.id).delete()
    db.commit()

    print("Generating correct 4-generation tree...")

    def create_person(first_name, gender, is_deceased=False, last_name="Chihala"):
        p = Person(
            id=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            is_deceased=is_deceased,
            created_by_user_id=user.id
        )
        db.add(p)
        return p

    def create_rel(p1_id, p2_id, rel_type):
        r = Relationship(
            id=uuid.uuid4(),
            person_a_id=p1_id,
            person_b_id=p2_id,
            relationship_type=rel_type,
            is_current=True,
            created_by_user_id=user.id
        )
        db.add(r)
        return r

    # GEN 1: Grandparents
    dada = create_person("Dada (Grandfather)", "male", is_deceased=True)
    dadi = create_person("Dadi (Grandmother)", "female", is_deceased=True)
    create_rel(dada.id, dadi.id, "spouse")

    # GEN 2: Father & Mother
    father = create_person("Father", "male")
    mother = create_person("Mother", "female", last_name="Unknown")
    create_rel(father.id, mother.id, "spouse")
    create_rel(dada.id, father.id, "parent")  # Dada is parent of Father
    create_rel(dadi.id, father.id, "parent")  # Dadi is parent of Father

    # Connect Father and Mother to Vatsal (GEN 3)
    create_rel(father.id, vatsal.id, "parent") # Father is parent of Vatsal
    create_rel(mother.id, vatsal.id, "parent") # Mother is parent of Vatsal

    # GEN 2: 4 Uncles & 3 Aunts
    for i in range(1, 5):
        uncle = create_person(f"Uncle {i}", "male")
        create_rel(dada.id, uncle.id, "parent")
        create_rel(dadi.id, uncle.id, "parent")
        
        aunt_in_law = create_person(f"Aunt (Uncle {i} Wife)", "female", last_name="Unknown")
        create_rel(uncle.id, aunt_in_law.id, "spouse")

        # GEN 3: Uncle's Sons (Cousins)
        for j in range(1, 3):
            cousin = create_person(f"Cousin Son {i}.{j}", "male")
            create_rel(uncle.id, cousin.id, "parent")
            create_rel(aunt_in_law.id, cousin.id, "parent")

            cousin_wife = create_person(f"Cousin {i}.{j} Wife", "female", last_name="Unknown")
            create_rel(cousin.id, cousin_wife.id, "spouse")

            # GEN 4: Cousin's Son (Nephew/Grand-nephew level)
            nephew = create_person(f"Nephew {i}.{j}.1", "male")
            create_rel(cousin.id, nephew.id, "parent")
            create_rel(cousin_wife.id, nephew.id, "parent")

    for i in range(1, 4):
        aunt = create_person(f"Aunt {i}", "female")
        create_rel(dada.id, aunt.id, "parent")
        create_rel(dadi.id, aunt.id, "parent")
        
        uncle_in_law = create_person(f"Uncle (Aunt {i} Husband)", "male", last_name="Unknown")
        create_rel(aunt.id, uncle_in_law.id, "spouse")

        # GEN 3: Aunt's Children
        cousin_m = create_person(f"Cousin Son {i}", "male", last_name="Unknown")
        create_rel(aunt.id, cousin_m.id, "parent")
        create_rel(uncle_in_law.id, cousin_m.id, "parent")

        cousin_f = create_person(f"Cousin Daughter {i}", "female", last_name="Unknown")
        create_rel(aunt.id, cousin_f.id, "parent")
        create_rel(uncle_in_law.id, cousin_f.id, "parent")

    # Add a Family group and put everyone in it so it shows on the Dashboard
    fam = Family(id=uuid.uuid4(), name="Chihala Family", created_by_user_id=user.id)
    db.add(fam)
    
    all_people = db.query(Person).all()
    for p in all_people:
        fm = FamilyMember(
            family_id=fam.id,
            person_id=p.id,
            role="owner" if p.id == vatsal.id else "member"
        )
        db.add(fm)

    db.commit()
    print("Tree generated successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)
finally:
    db.close()
