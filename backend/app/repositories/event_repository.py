import uuid
from typing import List, Optional, Tuple, Sequence
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import Session

from app.db.models.event import Event, EventTarget, EventParticipant

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: Event) -> Event:
        self.db.add(event)
        self.db.flush()
        return event

    def get_event(self, event_id: uuid.UUID) -> Optional[Event]:
        return self.db.execute(select(Event).where(Event.id == event_id)).scalar_one_or_none()

    def add_targets(self, targets: List[EventTarget]):
        self.db.add_all(targets)
        self.db.flush()
        
    def add_participants(self, participants: List[EventParticipant]):
        self.db.add_all(participants)
        self.db.flush()

    def get_event_with_targets(self, event_id: uuid.UUID) -> Optional[Tuple[Event, Sequence[EventTarget]]]:
        event = self.get_event(event_id)
        if not event:
            return None
        targets = self.db.execute(select(EventTarget).where(EventTarget.event_id == event_id)).scalars().all()
        return event, targets
        
    def delete_targets_for_event(self, event_id: uuid.UUID):
        self.db.execute(EventTarget.__table__.delete().where(EventTarget.event_id == event_id))
        self.db.flush()

    def list_events(self, user_id: uuid.UUID, user_family_ids: List[uuid.UUID], user_person_id: Optional[uuid.UUID],
                    limit: int = 20, offset: int = 0, event_type: str = None, upcoming: bool = False) -> Tuple[List[Event], int]:
        
        # Base query for visibility
        visibility_conditions = [
            Event.created_by_user_id == user_id,
            EventTarget.user_id == user_id
        ]
        if user_family_ids:
            visibility_conditions.append(EventTarget.family_id.in_(user_family_ids))
        if user_person_id:
            visibility_conditions.append(EventTarget.person_id == user_person_id)
            
        stmt = select(Event).distinct().join(EventTarget, Event.id == EventTarget.event_id, isouter=True)
        stmt = stmt.where(or_(*visibility_conditions))
        
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
            
        if upcoming:
            # We assume events end in the future
            from datetime import datetime, timezone, date
            now = datetime.now(timezone.utc)
            today = now.date()
            stmt = stmt.where(or_(
                Event.end_datetime >= now,
                Event.end_date >= today
            ))
            stmt = stmt.order_by(Event.start_datetime.asc().nulls_last(), Event.start_date.asc().nulls_last())
        else:
            stmt = stmt.order_by(desc(Event.created_at))

        total = self.db.execute(select(func.count(Event.id.distinct())).join(EventTarget, Event.id == EventTarget.event_id, isouter=True).where(or_(*visibility_conditions))).scalar_one()
        
        stmt = stmt.offset(offset).limit(limit)
        events = self.db.execute(stmt).scalars().all()
        return list(events), total

    def delete_event(self, event: Event):
        self.db.delete(event)
        self.db.flush()

    def add_participant(self, participant: EventParticipant):
        self.db.add(participant)
        self.db.flush()
        
    def get_participant(self, event_id: uuid.UUID, person_id: uuid.UUID) -> Optional[EventParticipant]:
        return self.db.execute(select(EventParticipant).where(
            EventParticipant.event_id == event_id,
            EventParticipant.person_id == person_id
        )).scalar_one_or_none()
        
    def list_participants(self, event_id: uuid.UUID, limit: int = 20, offset: int = 0) -> Tuple[List[EventParticipant], int]:
        total = self.db.execute(select(func.count()).where(EventParticipant.event_id == event_id)).scalar_one()
        stmt = select(EventParticipant).where(EventParticipant.event_id == event_id).order_by(EventParticipant.created_at.desc()).offset(offset).limit(limit)
        items = self.db.execute(stmt).scalars().all()
        return list(items), total

    def delete_participant(self, participant: EventParticipant):
        self.db.delete(participant)
        self.db.flush()
