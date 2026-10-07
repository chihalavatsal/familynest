import uuid
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.person import Person
from app.db.models.relationship import Relationship
from app.db.models.employment import Employment
from app.schemas.event import EventResponse
from app.services.authz_service import AuthzService

class LifeEventsService:
    def __init__(self, db: Session):
        self.db = db
        self.authz = AuthzService(db)

    def get_upcoming_events(self, user_id: uuid.UUID, days: int = 30) -> list[EventResponse]:
        # 1. Get all accessible people for this user
        accessible_people_ids = self.authz.get_accessible_people(user_id)
        if not accessible_people_ids:
            return []

        people = self.db.execute(select(Person).where(Person.id.in_(accessible_people_ids))).scalars().all()
        people_map = {p.id: p for p in people}

        relationships = self.db.execute(select(Relationship).where(
            Relationship.person_a_id.in_(accessible_people_ids),
            Relationship.person_b_id.in_(accessible_people_ids),
            Relationship.relationship_type == "spouse",
            Relationship.is_current == True,
            Relationship.start_date.is_not(None)
        )).scalars().all()

        employments = self.db.execute(select(Employment).where(
            Employment.person_id.in_(accessible_people_ids),
            Employment.start_date.is_not(None)
        )).scalars().all()

        today = date.today()
        cutoff = today + timedelta(days=days)

        events = []

        def get_next_occurrence(original_date: date) -> date:
            # handle leap year 29 Feb
            try:
                next_date = original_date.replace(year=today.year)
            except ValueError:
                next_date = original_date.replace(year=today.year, month=3, day=1)
                
            if next_date < today:
                try:
                    next_date = original_date.replace(year=today.year + 1)
                except ValueError:
                    next_date = original_date.replace(year=today.year + 1, month=3, day=1)
            return next_date

        def add_event(person, event_type, title, original_date):
            next_date = get_next_occurrence(original_date)
            if today <= next_date <= cutoff:
                events.append(EventResponse(
                    id=uuid.uuid5(uuid.NAMESPACE_OID, f"{person.id}-{event_type}-{next_date.year}"),
                    event_type=event_type,
                    title=title,
                    description=None,
                    start_date=next_date,
                    end_date=next_date,
                    all_day=True,
                    status="active",
                    person_id=person.id,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                ))

        for p in people:
            name = f"{p.first_name} {p.last_name or ''}".strip()
            if p.date_of_birth and not p.is_deceased:
                add_event(p, "birthday", f"{name}'s Birthday", p.date_of_birth)
            if p.date_of_death and p.is_deceased:
                add_event(p, "remembrance", f"Remembrance: {name}", p.date_of_death)

        # Spouses
        # Ensure we don't duplicate for A->B and B->A
        seen_marriages = set()
        for r in relationships:
            key = frozenset([r.person_a_id, r.person_b_id])
            if key in seen_marriages:
                continue
            seen_marriages.add(key)
            
            p_a = people_map.get(r.person_a_id)
            p_b = people_map.get(r.person_b_id)
            if p_a and p_b and r.start_date:
                name_a = p_a.first_name
                name_b = p_b.first_name
                add_event(p_a, "anniversary", f"{name_a} & {name_b}'s Anniversary", r.start_date)

        # Work anniversaries
        for emp in employments:
            p = people_map.get(emp.person_id)
            if p and not p.is_deceased and emp.start_date:
                name = f"{p.first_name} {p.last_name or ''}".strip()
                add_event(p, "work_anniversary", f"{name}'s Work Anniversary at {emp.employer_name}", emp.start_date)

        # Sort chronologically
        events.sort(key=lambda e: e.start_date)
        return events
