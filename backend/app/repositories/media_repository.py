import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.media import Media, MediaPerson, EventMedia

class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, media_id: uuid.UUID) -> Optional[Media]:
        stmt = select(Media).where(Media.id == media_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_for_family(self, family_id: uuid.UUID) -> List[Media]:
        stmt = select(Media).where(Media.family_id == family_id).order_by(Media.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, media: Media) -> Media:
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def update(self, media: Media) -> Media:
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def delete(self, media: Media) -> None:
        self.db.delete(media)
        self.db.commit()

    def add_person(self, media_id: uuid.UUID, person_id: uuid.UUID) -> None:
        link = MediaPerson(media_id=media_id, person_id=person_id)
        self.db.merge(link)
        self.db.commit()

    def remove_person(self, media_id: uuid.UUID, person_id: uuid.UUID) -> None:
        stmt = select(MediaPerson).where(MediaPerson.media_id == media_id, MediaPerson.person_id == person_id)
        link = self.db.execute(stmt).scalar_one_or_none()
        if link:
            self.db.delete(link)
            self.db.commit()

    def associate_event(self, media_id: uuid.UUID, event_id: uuid.UUID) -> None:
        link = EventMedia(event_id=event_id, media_id=media_id)
        self.db.merge(link)
        self.db.commit()
