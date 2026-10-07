import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.album import Album, AlbumMedia

class AlbumRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, album_id: uuid.UUID) -> Optional[Album]:
        stmt = select(Album).where(Album.id == album_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_all_for_family(self, family_id: uuid.UUID) -> List[Album]:
        stmt = select(Album).where(Album.family_id == family_id).order_by(Album.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def create(self, album: Album) -> Album:
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        return album

    def update(self, album: Album) -> Album:
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        return album

    def delete(self, album: Album) -> None:
        self.db.delete(album)
        self.db.commit()

    def add_media(self, album_id: uuid.UUID, media_id: uuid.UUID) -> None:
        link = AlbumMedia(album_id=album_id, media_id=media_id)
        self.db.merge(link)
        self.db.commit()

    def remove_media(self, album_id: uuid.UUID, media_id: uuid.UUID) -> None:
        stmt = select(AlbumMedia).where(AlbumMedia.album_id == album_id, AlbumMedia.media_id == media_id)
        link = self.db.execute(stmt).scalar_one_or_none()
        if link:
            self.db.delete(link)
            self.db.commit()
