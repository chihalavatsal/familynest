import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from typing import List
from datetime import date

from app.db.models.person import Person
from app.db.models.relationship import Relationship
from app.db.models.employment import Employment
from app.db.models.education import Education
from app.schemas.timeline import TimelineEvent
from app.services.authz_service import AuthzService

class TimelineService:
    def __init__(self, db: Session):
        self.db = db
        self.authz = AuthzService(db)

    def get_timeline(self, person_id: uuid.UUID, user_id: uuid.UUID) -> List[TimelineEvent]:
        # 1. Verify access
        if not self.authz.can_read_person(user_id, person_id):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Person not found")
            
        person = self.db.execute(select(Person).where(Person.id == person_id)).scalar_one()
        
        events = []
        
        # Birth
        if person.date_of_birth:
            events.append(TimelineEvent(
                id=uuid.uuid4(),
                date=person.date_of_birth,
                year=person.date_of_birth.year,
                title="Born",
                description=f"Born in {person.birth_place}" if person.birth_place else None,
                icon="birth"
            ))
            
        # Death
        if person.date_of_death and person.is_deceased:
            events.append(TimelineEvent(
                id=uuid.uuid4(),
                date=person.date_of_death,
                year=person.date_of_death.year,
                title="Passed away",
                description=f"in {person.death_place}" if person.death_place else None,
                icon="death"
            ))
            
        # Education
        educations = self.db.execute(select(Education).where(Education.person_id == person_id)).scalars().all()
        for ed in educations:
            if ed.start_date:
                events.append(TimelineEvent(
                    id=ed.id,
                    date=ed.start_date,
                    year=ed.start_date.year,
                    title=f"Started at {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
            if ed.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=ed.end_date,
                    year=ed.end_date.year,
                    title=f"Graduated from {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
            if not ed.start_date and not ed.end_date:
                events.append(TimelineEvent(
                    id=ed.id,
                    date=None,
                    year=None,
                    title=f"Studied at {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
                
        # Employment
        employments = self.db.execute(select(Employment).where(Employment.person_id == person_id)).scalars().all()
        for emp in employments:
            if emp.start_date:
                events.append(TimelineEvent(
                    id=emp.id,
                    date=emp.start_date,
                    year=emp.start_date.year,
                    title=f"Started working at {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
            if emp.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=emp.end_date,
                    year=emp.end_date.year,
                    title=f"Left {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
            if not emp.start_date and not emp.end_date:
                events.append(TimelineEvent(
                    id=emp.id,
                    date=None,
                    year=None,
                    title=f"Worked at {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
                
        # Relationships (Marriage & Children)
        # To get children, we need relationships where person_id is a parent
        # If person_id is person_a and relationship_type is 'parent', then person_b is the child!
        # If person_id is person_b and relationship_type is 'parent', then person_a is the child!
        # Wait, the relationship graph service standardizes it?
        # Actually, if type='parent', person_a is the parent of person_b.
        children_rels = self.db.execute(
            select(Relationship).where(Relationship.person_a_id == person_id, Relationship.relationship_type == 'parent')
        ).scalars().all()
        
        if children_rels:
            child_ids = [r.person_b_id for r in children_rels]
            children = self.db.execute(select(Person).where(Person.id.in_(child_ids))).scalars().all()
            for child in children:
                if child.date_of_birth:
                    events.append(TimelineEvent(
                        id=child.id,
                        date=child.date_of_birth,
                        year=child.date_of_birth.year,
                        title=f"Child born",
                        description=f"{child.first_name} {child.last_name or ''}".strip(),
                        icon="child"
                    ))
                    
        # Spouses (Marriage)
        spouse_rels = self.db.execute(
            select(Relationship).where(
                or_(Relationship.person_a_id == person_id, Relationship.person_b_id == person_id),
                Relationship.relationship_type == 'spouse'
            )
        ).scalars().all()
        
        for sp in spouse_rels:
            if sp.start_date:
                other_id = sp.person_b_id if sp.person_a_id == person_id else sp.person_a_id
                other = self.db.execute(select(Person).where(Person.id == other_id)).scalar_one_or_none()
                if other:
                    events.append(TimelineEvent(
                        id=sp.id,
                        date=sp.start_date,
                        year=sp.start_date.year,
                        title="Got married",
                        description=f"To {other.first_name} {other.last_name or ''}".strip(),
                        icon="marriage"
                    ))
        
        # Sort events by date (if missing date, try to put at end or sort by year)
        def get_sort_key(e: TimelineEvent):
            if e.date:
                return e.date
            if e.year:
                return date(e.year, 1, 1)
            return date.max
            
        events.sort(key=get_sort_key)
        return events
