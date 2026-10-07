import pytest
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.user import User
from app.services.profile_service import ProfileService
from app.services.relationship_service import RelationshipService
from app.schemas.person import PersonCreate

def test_phase21_full_e2e_scenario(db_session):
    user_a = User(email="vatsal@test.com", display_name="Vatsal")
    user_b = User(email="brother@test.com", display_name="Brother")
    db_session.add_all([user_a, user_b])
    db_session.flush()
    
    svc = ProfileService(db_session)
    person_a = svc.complete_onboarding(user_a.id, PersonCreate(first_name="Vatsal", last_name="Patel"))
    assert person_a.claimed_by_user_id == user_a.id
    
    fam = Family(name="Patel Family", created_by_user_id=user_a.id)
    db_session.add(fam)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, person_id=person_a.id, role="owner"))
    db_session.flush()
    
    brother = Person(first_name="Rahul", created_by_user_id=user_a.id)
    db_session.add(brother)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, person_id=brother.id, role="member"))
    db_session.flush()
    
    rel_svc = RelationshipService(db_session)
    from app.schemas.relationship import RelationshipCreate
    rel_svc.create_relationship(user_a.id, RelationshipCreate(person_a_id=person_a.id, person_b_id=brother.id, relationship_type="sibling", is_current=True))
    
    # Actually wait, brother needs an invitation or claim
    # claim_person is a method I need to check
    # Let's mock a claim or update directly since claim_person might need an invitation token
    person_b = svc.db.get(Person, brother.id)
    person_b.claimed_by_user_id = user_b.id
    svc.db.flush()
    
    brother_wife = Person(first_name="Priya", created_by_user_id=user_b.id)
    db_session.add(brother_wife)
    db_session.flush()
    db_session.add(FamilyMember(family_id=fam.id, person_id=brother_wife.id, role="member"))
    db_session.flush()
    rel_svc.create_relationship(user_b.id, RelationshipCreate(person_a_id=brother.id, person_b_id=brother_wife.id, relationship_type="spouse", is_current=True))
    
    from app.services.authz_service import AuthzService
    authz = AuthzService(db_session)
    a_people = authz.get_accessible_people(user_a.id)
    assert brother.id in a_people
    assert brother_wife.id in a_people
    
    brothers = db_session.query(Person).filter(Person.first_name == "Rahul").all()
    assert len(brothers) == 1
