"""Database Foundation & Integrity Test Suite for FamilyNest.

Uses transactional rollbacks to test against PostgreSQL without polluting or
destroying persistent data.
"""
import uuid
import pytest
from datetime import datetime, date, timezone
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.db.database import engine, SessionLocal, get_redacted_database_url
from app.core.config import settings
from app.db.models import (
    User,
    Person,
    Family,
    FamilyMember,
    Relationship,
    Invitation,
    AuditLog,
)





# 1. Database Connection Test
def test_database_connection():
    """Verify backend can connect to configured PostgreSQL database."""
    redacted_url = get_redacted_database_url(settings.DATABASE_URL or "")
    print(f"\n[Test] Connecting to database: {redacted_url}")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1;")).scalar()
        assert result == 1
        version_str = conn.execute(text("SELECT version();")).scalar()
        assert version_str is not None
        print(f"[Test] Database verified: {version_str[:50]}...")


# 2. Users Table Test
def test_create_user(db_session):
    """Verify user account creation."""
    user = User(
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        display_name="Test User",
        is_active=True,
        is_verified=False,
    )
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    assert user.created_at is not None
    assert user.is_active is True


# 3. People Table & User/Person Distinction
def test_person_exists_without_user(db_session):
    """Verify a Person can exist without a User account (unclaimed family member)."""
    person = Person(
        first_name="Ramesh",
        last_name="Patel",
        gender="male",
        profile_status="unclaimed",
        claimed_by_user_id=None,
    )
    db_session.add(person)
    db_session.flush()

    assert person.id is not None
    assert person.claimed_by_user_id is None
    assert person.profile_status == "unclaimed"


def test_user_claims_existing_person(db_session):
    """Verify a User can claim an existing Person record without duplication."""
    user = User(email=f"claim_{uuid.uuid4().hex[:8]}@example.com")
    db_session.add(user)
    db_session.flush()

    person = Person(
        first_name="Sita",
        last_name="Patel",
        profile_status="unclaimed",
    )
    db_session.add(person)
    db_session.flush()

    # Claim person
    person.claimed_by_user_id = user.id
    person.profile_status = "claimed"
    db_session.flush()

    assert person.claimed_by_user_id == user.id
    assert person.profile_status == "claimed"


# 4. Deceased Person Test
def test_deceased_person_remains_valid(db_session):
    """Verify deceased family member remains a valid permanent person record."""
    ancestor = Person(
        first_name="Harilal",
        last_name="Patel",
        date_of_birth=date(1920, 5, 10),
        date_of_death=date(1995, 11, 20),
        is_deceased=True,
        profile_status="deceased",
    )
    db_session.add(ancestor)
    db_session.flush()

    assert ancestor.id is not None
    assert ancestor.is_deceased is True
    assert ancestor.date_of_death == date(1995, 11, 20)


# 5. Families & Multiple Family Networks
def test_person_in_multiple_family_networks(db_session):
    """Verify one Person can belong to multiple family networks (e.g. maternal and in-laws)."""
    creator = User(email=f"creator_{uuid.uuid4().hex[:8]}@example.com")
    db_session.add(creator)
    db_session.flush()

    person = Person(first_name="Aarav", last_name="Sharma")
    fam1 = Family(name="Paternal Sharma Family", created_by_user_id=creator.id)
    fam2 = Family(name="Maternal Verma Family", created_by_user_id=creator.id)
    db_session.add_all([person, fam1, fam2])
    db_session.flush()

    mem1 = FamilyMember(family_id=fam1.id, person_id=person.id, role="member")
    mem2 = FamilyMember(family_id=fam2.id, person_id=person.id, role="admin")
    db_session.add_all([mem1, mem2])
    db_session.flush()

    memberships = db_session.query(FamilyMember).filter_by(person_id=person.id).all()
    assert len(memberships) == 2


def test_duplicate_family_membership_rejection(db_session):
    """Verify duplicate membership in the same family is rejected."""
    creator = User(email=f"dup_{uuid.uuid4().hex[:8]}@example.com")
    db_session.add(creator)
    db_session.flush()

    person = Person(first_name="Pooja", last_name="Joshi")
    fam = Family(name="Joshi Family", created_by_user_id=creator.id)
    db_session.add_all([person, fam])
    db_session.flush()

    mem1 = FamilyMember(family_id=fam.id, person_id=person.id, role="member")
    db_session.add(mem1)
    db_session.flush()

    mem2 = FamilyMember(family_id=fam.id, person_id=person.id, role="member")
    db_session.add(mem2)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


# 6. Relationships & Historical Records
def test_historical_relationships_preserved(db_session):
    """Verify relationships can capture divorce/marriage changes over time without deletion."""
    creator = User(email=f"hist_{uuid.uuid4().hex[:8]}@example.com")
    p_a = Person(first_name="Dev", last_name="Kapoor")
    p_b = Person(first_name="Maya", last_name="Kapoor")
    p_c = Person(first_name="Ananya", last_name="Kapoor")
    db_session.add_all([creator, p_a, p_b, p_c])
    db_session.flush()

    # Historical marriage: Dev & Maya (now divorced)
    rel1 = Relationship(
        person_a_id=p_a.id,
        person_b_id=p_b.id,
        relationship_type="divorced_spouse",
        start_date=date(2010, 1, 1),
        end_date=date(2018, 6, 1),
        is_current=False,
        created_by_user_id=creator.id,
    )
    # Current marriage: Dev & Ananya
    rel2 = Relationship(
        person_a_id=p_a.id,
        person_b_id=p_c.id,
        relationship_type="spouse",
        start_date=date(2020, 2, 14),
        is_current=True,
        created_by_user_id=creator.id,
    )
    db_session.add_all([rel1, rel2])
    db_session.flush()

    rels = db_session.query(Relationship).filter_by(person_a_id=p_a.id).all()
    assert len(rels) == 2


# 7. Constraint Tests
def test_self_relationship_rejection(db_session):
    """Verify self-relationship is rejected by database check constraint."""
    creator = User(email=f"self_{uuid.uuid4().hex[:8]}@example.com")
    person = Person(first_name="Self", last_name="Referential")
    db_session.add_all([creator, person])
    db_session.flush()

    rel = Relationship(
        person_a_id=person.id,
        person_b_id=person.id,
        relationship_type="sibling",
        created_by_user_id=creator.id,
    )
    db_session.add(rel)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_invalid_relationship_type_rejection(db_session):
    """Verify derived/invalid relationship type is rejected (e.g. 'cousin' or 'uncle')."""
    creator = User(email=f"rel_{uuid.uuid4().hex[:8]}@example.com")
    p1 = Person(first_name="Amit", last_name="Kumar")
    p2 = Person(first_name="Vijay", last_name="Kumar")
    db_session.add_all([creator, p1, p2])
    db_session.flush()

    rel = Relationship(
        person_a_id=p1.id,
        person_b_id=p2.id,
        relationship_type="uncle",  # Invalid! Derived relationships are not stored
        created_by_user_id=creator.id,
    )
    db_session.add(rel)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_invalid_profile_status_rejection(db_session):
    """Verify invalid profile_status is rejected by database check constraint."""
    person = Person(
        first_name="Invalid",
        last_name="Status",
        profile_status="random_status",
    )
    db_session.add(person)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_invalid_invitation_status_rejection(db_session):
    """Verify invalid invitation status is rejected."""
    creator = User(email=f"inv_{uuid.uuid4().hex[:8]}@example.com")
    person = Person(first_name="Inv", last_name="Person")
    db_session.add_all([creator, person])
    db_session.flush()

    inv = Invitation(
        person_id=person.id,
        invited_by_user_id=creator.id,
        invitation_token="token_abc_123",
        status="bogus_status",
    )
    db_session.add(inv)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


# 8. Invitations & Audit Logs
def test_create_invitation_and_audit_log(db_session):
    """Verify invitations and audit logs with JSONB metadata."""
    creator = User(email=f"audit_{uuid.uuid4().hex[:8]}@example.com")
    person = Person(first_name="Kiran", last_name="Shah")
    db_session.add_all([creator, person])
    db_session.flush()

    invitation = Invitation(
        person_id=person.id,
        invited_by_user_id=creator.id,
        invited_email="kiran@example.com",
        invitation_token=uuid.uuid4().hex,
        status="pending",
    )
    audit = AuditLog(
        actor_user_id=creator.id,
        action="INVITATION_CREATED",
        entity_type="invitation",
        entity_id=invitation.id,
        metadata_={"method": "email", "ip": "127.0.0.1"},
    )
    db_session.add_all([invitation, audit])
    db_session.flush()

    assert invitation.id is not None
    assert audit.id is not None
    assert audit.metadata_["method"] == "email"
