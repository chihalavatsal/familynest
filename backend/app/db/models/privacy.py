import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.models.base import Base

class PersonPrivacySettings(Base):
    __tablename__ = "person_privacy_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    phone_visibility = Column(String, default="private", nullable=False)
    email_visibility = Column(String, default="private", nullable=False)
    dob_visibility = Column(String, default="private", nullable=False)
    bio_visibility = Column(String, default="family", nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    person = relationship("Person")


class FamilyPrivacySettings(Base):
    __tablename__ = "family_privacy_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    allow_member_discovery = Column(Boolean, default=True, nullable=False)
    default_content_visibility = Column(String, default="family", nullable=False)
    member_invites_role = Column(String, default="member", nullable=False)
    member_management_role = Column(String, default="admin", nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    family = relationship("Family")
