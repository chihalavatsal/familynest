import uuid
from sqlalchemy.orm import Session
from app.repositories.activity_repository import ActivityRepository

class ActivityService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ActivityRepository(db)

    def _get_user_context(self, user_id: uuid.UUID):
        from app.db.models.person import Person
        from app.db.models.family import FamilyMember
        from sqlalchemy import select
        person = self.db.execute(select(Person).where(Person.claimed_by_user_id == user_id)).scalar_one_or_none()
        person_id = person.id if person else None
        family_ids = []
        if person_id:
            family_ids = self.db.execute(select(FamilyMember.family_id).where(FamilyMember.person_id == person_id)).scalars().all()
        return person_id, list(family_ids)

    def list_activities(self, user_id: uuid.UUID, family_id: uuid.UUID = None, limit: int = 20, offset: int = 0):
        person_id, family_ids = self._get_user_context(user_id)
        return self.repo.list_activities(user_id, family_ids, person_id, family_id, limit, offset)
