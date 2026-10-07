import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    visibility = Column(String, default="family", nullable=False)
    memory_date = Column(Date, nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    family = relationship("Family")
    created_by = relationship("User")
    tagged_people = relationship("MemoryPerson", back_populates="memory", cascade="all, delete-orphan")
    media = relationship("MemoryMedia", back_populates="memory", cascade="all, delete-orphan")


class MemoryPerson(Base):
    __tablename__ = "memory_people"

    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), primary_key=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    memory = relationship("Memory", back_populates="tagged_people")
    person = relationship("Person")


class MemoryMedia(Base):
    __tablename__ = "memory_media"

    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True)
    media_id = Column(UUID(as_uuid=True), ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    memory = relationship("Memory", back_populates="media")
    media = relationship("Media")

class MemoryAllowedUser(Base):
    __tablename__ = "memory_allowed_users"

    memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    memory = relationship("Memory")
    user = relationship("User")
