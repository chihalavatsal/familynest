import uuid
from typing import List, Tuple
from sqlalchemy import select, func, desc, or_, and_
from sqlalchemy.orm import Session

from app.db.models.activity import Activity
from app.db.models.event import Event, EventTarget

class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_activity(self, activity: Activity) -> Activity:
        self.db.add(activity)
        self.db.flush()
        return activity

    def list_activities(self, user_id: uuid.UUID, user_family_ids: List[uuid.UUID], user_person_id: uuid.UUID,
                        family_id: uuid.UUID = None, limit: int = 20, offset: int = 0) -> Tuple[List[Activity], int]:
        
        stmt = select(Activity).distinct()
        
        # We need to filter activities by visibility
        # Activity visibility is tied to the underlying entity
        # For this phase, we support 'event' and 'family_member' and 'person' maybe.
        # Simplest: if activity.family_id is set, check if user is in that family.
        # Otherwise, if entity is event, check event targets.
        
        conditions = []
        
        if family_id:
            # explicit family feed
            if family_id not in user_family_ids:
                return [], 0
            conditions.append(Activity.family_id == family_id)
        else:
            if user_family_ids:
                conditions.append(Activity.family_id.in_(user_family_ids))
            
            # Plus events targeted directly at the user
            stmt = stmt.outerjoin(Event, Activity.entity_id == Event.id).outerjoin(EventTarget, Event.id == EventTarget.event_id)
            
            event_visibility = and_(
                Activity.entity_type == 'event',
                or_(
                    Event.created_by_user_id == user_id,
                    EventTarget.user_id == user_id,
                    EventTarget.person_id == user_person_id if user_person_id else False,
                    EventTarget.family_id.in_(user_family_ids) if user_family_ids else False
                )
            )
            conditions.append(event_visibility)
            
            # Plus actor is user
            conditions.append(Activity.actor_user_id == user_id)
        
        stmt = stmt.where(or_(*conditions)).order_by(desc(Activity.created_at))
        
        total_stmt = select(func.count(Activity.id.distinct())).outerjoin(Event, Activity.entity_id == Event.id).outerjoin(EventTarget, Event.id == EventTarget.event_id).where(or_(*conditions))
        total = self.db.execute(total_stmt).scalar_one()
        
        stmt = stmt.offset(offset).limit(limit)
        items = self.db.execute(stmt).scalars().all()
        return list(items), total
