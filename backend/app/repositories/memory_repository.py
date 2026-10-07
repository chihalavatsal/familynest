import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.memory import Memory, MemoryPerson, MemoryMedia
from app.db.models.family import FamilyMember

class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, memory_id: uuid.UUID) -> Optional[Memory]:
        stmt = select(Memory).where(Memory.id == memory_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_for_family(self, family_id: uuid.UUID) -> List[Memory]:
        stmt = select(Memory).where(Memory.family_id == family_id).order_by(Memory.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, memory: Memory) -> Memory:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def update(self, memory: Memory) -> Memory:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def delete(self, memory: Memory) -> None:
        self.db.delete(memory)
        self.db.commit()

    def add_person(self, memory_id: uuid.UUID, person_id: uuid.UUID) -> None:
        link = MemoryPerson(memory_id=memory_id, person_id=person_id)
        self.db.merge(link)
        self.db.commit()

    def remove_person(self, memory_id: uuid.UUID, person_id: uuid.UUID) -> None:
        stmt = select(MemoryPerson).where(MemoryPerson.memory_id == memory_id, MemoryPerson.person_id == person_id)
        link = self.db.execute(stmt).scalar_one_or_none()
        if link:
            self.db.delete(link)
            self.db.commit()

    def add_media(self, memory_id: uuid.UUID, media_id: uuid.UUID) -> None:
        link = MemoryMedia(memory_id=memory_id, media_id=media_id)
        self.db.merge(link)
        self.db.commit()

    def remove_media(self, memory_id: uuid.UUID, media_id: uuid.UUID) -> None:
        stmt = select(MemoryMedia).where(MemoryMedia.memory_id == memory_id, MemoryMedia.media_id == media_id)
        link = self.db.execute(stmt).scalar_one_or_none()
        if link:
            self.db.delete(link)
            self.db.commit()

    def user_has_family_access(self, user_id: uuid.UUID, family_id: uuid.UUID) -> bool:
        stmt = select(FamilyMember).where(FamilyMember.user_id == user_id, FamilyMember.family_id == family_id)
        return self.db.execute(stmt).scalar_one_or_none() is not None
