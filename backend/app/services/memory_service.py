import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.memory import Memory
from app.db.models.activity import Activity
from app.db.models.audit_log import AuditLog
from app.repositories.memory_repository import MemoryRepository
from app.services.authz_service import AuthzService
from app.db.models.memory import MemoryAllowedUser

class MemoryService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MemoryRepository(db)
        self.authz = AuthzService(db)



    def create(self, memory_data, user_id: uuid.UUID) -> Memory:
        self.authz.require_family_view(user_id, memory_data.family_id)
        mem = Memory(
            family_id=memory_data.family_id,
            title=memory_data.title,
            body=memory_data.body,
            memory_date=memory_data.memory_date,
            created_by_user_id=user_id,
            visibility=getattr(memory_data, 'visibility', 'family')
        )
        self.repo.create(mem)
        
        # Log Audit
        self.db.add(AuditLog(actor_user_id=user_id, action="memory.create", entity_type="memory", entity_id=mem.id))
        
        # Activity
        self.db.add(Activity(
            actor_user_id=user_id,
            family_id=mem.family_id,
            entity_type="memory",
            entity_id=mem.id,
            action_type="create",
            title=f"Added a memory: {mem.title}"
        ))
        self.db.commit()
        return mem

    def get_by_id(self, memory_id: uuid.UUID, user_id: uuid.UUID) -> Memory:
        mem = self.repo.get_by_id(memory_id)
        if not mem:
            raise HTTPException(status_code=404, detail="Memory not found.")
        self.authz.require_memory_view(user_id, mem)
        return mem

    def list_for_family(self, family_id: uuid.UUID, user_id: uuid.UUID) -> List[Memory]:
        self.authz.require_family_view(user_id, family_id)
        return self.repo.get_all_for_family(family_id)

    def update(self, memory_id: uuid.UUID, memory_data, user_id: uuid.UUID) -> Memory:
        mem = self.get_by_id(memory_id, user_id)
        if memory_data.title is not None:
            mem.title = memory_data.title
        if memory_data.body is not None:
            mem.body = memory_data.body
        if memory_data.memory_date is not None:
            mem.memory_date = memory_data.memory_date
        
        self.repo.update(mem)
        self.db.add(AuditLog(actor_user_id=user_id, action="memory.update", entity_type="memory", entity_id=mem.id))
        self.db.commit()
        return mem

    def delete(self, memory_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = self.get_by_id(memory_id, user_id)
        self.repo.delete(mem)
        self.db.add(AuditLog(actor_user_id=user_id, action="memory.delete", entity_type="memory", entity_id=mem.id))
        self.db.commit()

    def add_person(self, memory_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = self.get_by_id(memory_id, user_id)
        self.repo.add_person(memory_id, person_id)

    def remove_person(self, memory_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = self.get_by_id(memory_id, user_id)
        self.repo.remove_person(memory_id, person_id)
        
    def add_media(self, memory_id: uuid.UUID, media_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = self.get_by_id(memory_id, user_id)
        self.repo.add_media(memory_id, media_id)
        
    def remove_media(self, memory_id: uuid.UUID, media_id: uuid.UUID, user_id: uuid.UUID) -> None:
        mem = self.get_by_id(memory_id, user_id)
        self.repo.remove_media(memory_id, media_id)
