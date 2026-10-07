import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.media import Media
from app.db.models.activity import Activity
from app.db.models.audit_log import AuditLog
from app.repositories.media_repository import MediaRepository
from app.services.authz_service import AuthzService
from app.services.storage_service import StorageService

class MediaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MediaRepository(db)
        self.authz = AuthzService(db)
        self.storage = StorageService()



    def create(self, media_data, user_id: uuid.UUID) -> Media:
        self.authz.require_family_view(user_id, media_data.family_id)
        
        media = Media(
            family_id=media_data.family_id,
            original_filename=media_data.original_filename,
            mime_type=media_data.mime_type,
            file_size=media_data.file_size,
            width=media_data.width,
            height=media_data.height,
            uploaded_by_user_id=user_id,
            status="pending"
        )
        self.repo.create(media)
        
        self.db.add(AuditLog(actor_user_id=user_id, action="media.create", entity_type="media", entity_id=media.id))
        self.db.commit()
        return media

    def get_by_id(self, media_id: uuid.UUID, user_id: uuid.UUID) -> Media:
        media = self.repo.get_by_id(media_id)
        if not media:
            raise HTTPException(status_code=404, detail="Media not found.")
        self.authz.require_family_view(user_id, media.family_id)
        return media

    def list_for_family(self, family_id: uuid.UUID, user_id: uuid.UUID) -> List[Media]:
        self.authz.require_family_view(user_id, family_id)
        return self.repo.get_all_for_family(family_id)

    def delete(self, media_id: uuid.UUID, user_id: uuid.UUID) -> None:
        media = self.get_by_id(media_id, user_id)
        
        # Delete from storage if available
        if media.storage_object_key:
            self.storage.delete_object(media.storage_object_key)
            
        self.repo.delete(media)
        self.db.add(AuditLog(actor_user_id=user_id, action="media.delete", entity_type="media", entity_id=media.id))
        self.db.commit()

    def add_person(self, media_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID) -> None:
        media = self.get_by_id(media_id, user_id)
        self.repo.add_person(media_id, person_id)

    def remove_person(self, media_id: uuid.UUID, person_id: uuid.UUID, user_id: uuid.UUID) -> None:
        media = self.get_by_id(media_id, user_id)
        self.repo.remove_person(media_id, person_id)

    def associate_event(self, media_id: uuid.UUID, event_id: uuid.UUID, user_id: uuid.UUID) -> None:
        media = self.get_by_id(media_id, user_id)
        self.repo.associate_event(media_id, event_id)
