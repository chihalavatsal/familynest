import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.album import AlbumAllowedUser, Album
from app.db.models.activity import Activity
from app.db.models.audit_log import AuditLog
from app.repositories.album_repository import AlbumRepository
from app.repositories.memory_repository import MemoryRepository
from app.services.authz_service import AuthzService

class AlbumService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AlbumRepository(db)
        self.authz = AuthzService(db)



    def create(self, album_data, user_id: uuid.UUID) -> Album:
        self.authz.require_family_view(user_id, album_data.family_id)
        album = Album(
            family_id=album_data.family_id,
            title=album_data.title,
            description=album_data.description,
            created_by_user_id=user_id,
            visibility=getattr(album_data, 'visibility', 'family')
        )
        self.repo.create(album)
        
        self.db.add(AuditLog(actor_user_id=user_id, action="album.create", entity_type="album", entity_id=album.id))
        self.db.add(Activity(
            actor_user_id=user_id,
            family_id=album.family_id,
            entity_type="album",
            entity_id=album.id,
            action_type="create",
            title=f"Created album: {album.title}"
        ))

        self.db.commit()
        
        # Handle allowed users
        if getattr(album_data, 'visibility', 'family') == 'selected_members' and getattr(album_data, 'allowed_user_ids', None):
            for uid in album_data.allowed_user_ids:
                if self.authz.can_view_family(uid, album_data.family_id):
                    self.db.add(AlbumAllowedUser(album_id=album.id, user_id=uid))
            self.db.commit()
            
        return album

    def get_by_id(self, album_id: uuid.UUID, user_id: uuid.UUID) -> Album:
        album = self.repo.get_by_id(album_id)
        if not album:
            raise HTTPException(status_code=404, detail="Album not found.")
        self.authz.require_album_view(user_id, album)
        return album

    def list_for_family(self, family_id: uuid.UUID, user_id: uuid.UUID) -> List[Album]:
        self.authz.require_family_view(user_id, family_id)
        return self.repo.get_all_for_family(family_id)

    def update(self, album_id: uuid.UUID, album_data, user_id: uuid.UUID) -> Album:
        album = self.get_by_id(album_id, user_id)
        if album_data.title is not None:
            album.title = album_data.title
        if album_data.description is not None:
            album.description = album_data.description
        
        self.repo.update(album)
        self.db.add(AuditLog(actor_user_id=user_id, action="album.update", entity_type="album", entity_id=album.id))
        self.db.commit()
        return album

    def delete(self, album_id: uuid.UUID, user_id: uuid.UUID) -> None:
        album = self.get_by_id(album_id, user_id)
        self.repo.delete(album)
        self.db.add(AuditLog(actor_user_id=user_id, action="album.delete", entity_type="album", entity_id=album.id))
        self.db.commit()

    def add_media(self, album_id: uuid.UUID, media_id: uuid.UUID, user_id: uuid.UUID) -> None:
        album = self.get_by_id(album_id, user_id)
        self.repo.add_media(album_id, media_id)
        
    def remove_media(self, album_id: uuid.UUID, media_id: uuid.UUID, user_id: uuid.UUID) -> None:
        album = self.get_by_id(album_id, user_id)
        self.repo.remove_media(album_id, media_id)
