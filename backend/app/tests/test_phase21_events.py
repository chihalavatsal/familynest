import pytest
from httpx import AsyncClient
from app.db.models.user import User
from app.db.models.family import Family, FamilyMember
from app.db.models.person import Person
from app.db.models.event import Event, EventTarget
from app.schemas.event import EventCreate
from app.services.event_service import EventService
import uuid
from datetime import datetime, timezone

def test_personal_event_isolation(db_session):
    u1 = User(email="eventowner@test.com", display_name="User1")
    u2 = User(email="eventviewer@test.com", display_name="User2")
    db_session.add_all([u1, u2])
    db_session.flush()
    
    p1 = Person(first_name="User", last_name="1", created_by_user_id=u1.id, claimed_by_user_id=u1.id)
    p2 = Person(first_name="User", last_name="2", created_by_user_id=u2.id, claimed_by_user_id=u2.id)
    db_session.add_all([p1, p2])
    db_session.flush()

    # User1 creates a personal event
    svc = EventService(db_session)
    from app.schemas.event import EventCreate, EventAudienceInput
    
    # Test 2 & 3: Only me, no family id required
    evt_data = EventCreate(
        title="My Private Secret",
        event_type="announcement",
        all_day=True,
        start_date="2026-01-01",
        end_date="2026-01-01",
        audience=EventAudienceInput(type="user")
    )
    
    evt = svc.create_event(u1.id, evt_data)
    assert evt is not None
    assert evt.title == "My Private Secret"
    
    # Check targets
    targets = db_session.query(EventTarget).filter(EventTarget.event_id == evt.id).all()
    assert len(targets) == 1
    assert targets[0].audience_type == "user"
    assert targets[0].user_id == u1.id
    
    # Test 4 & 5: Other user list/read
    # u2 should not see it
    events_u2, count_u2 = svc.list_events(u2.id)
    assert count_u2 == 0, f'count_u2 is {count_u2}, expected 0'
    assert len(events_u2) == 0
    
    # u1 should see it
    events_u1, count_u1 = svc.list_events(u1.id)
    assert count_u1 == 1
    assert events_u1[0].id == evt.id
    
    # User 2 direct read should fail
    with pytest.raises(Exception):
        svc.get_event(evt.id, u2.id)
        
    # Search isolation
    from app.services.search_service import SearchService
    search_svc = SearchService(db_session)
    
    # User 1 searches
    res1 = search_svc.search(u1.id, "Private Secret", type_filter="event")
    assert res1.total == 1
    assert res1.items[0].id == evt.id
    
    # User 2 searches
    res2 = search_svc.search(u2.id, "Private Secret", type_filter="event")
    assert res2.total == 0

def test_family_event_isolation(db_session):
    u1 = User(email="fam1@test.com", display_name="Fam1")
    db_session.add(u1)
    db_session.flush()
    
    p1 = Person(first_name="User", last_name="1", created_by_user_id=u1.id, claimed_by_user_id=u1.id)
    db_session.add(p1)
    db_session.flush()
    
    f1 = Family(name="Family One", created_by_user_id=u1.id)
    db_session.add(f1)
    db_session.flush()
    db_session.add(FamilyMember(family_id=f1.id, person_id=p1.id, role="owner"))
    db_session.flush()
    
    svc = EventService(db_session)
    from app.schemas.event import EventCreate, EventAudienceInput
    
    # Test 1: Family Event requires family_id
    with pytest.raises(Exception):
        svc.create_event(u1.id, EventCreate(
            title="Fam Missing ID",
            event_type="announcement",
            all_day=True,
            start_date="2026-01-01",
            end_date="2026-01-01",
            audience=EventAudienceInput(type="family")
        ))
        
    evt_data = EventCreate(
        title="Fam Correct",
        event_type="announcement",
        all_day=True,
        start_date="2026-01-01",
        end_date="2026-01-01",
        audience=EventAudienceInput(type="family", family_id=f1.id)
    )
    evt = svc.create_event(u1.id, evt_data)
    assert evt is not None
