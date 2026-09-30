import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base

ALLOWED_FAMILY_ROLES = ('owner', 'admin', 'member', 'invited')


class Family(Base):
    """Families entity: Represents an independent family network circle.
    
    CRITICAL FAMILY NETWORK RULE:
    Marriage or kinship links between people do NOT merge two family networks.
    A person can belong to multiple family networks (e.g. Mother's Family, Father's Family,
    Spouse's Family). Each family network remains an independent hub.
    """
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    # Creator must not be deleted if family network exists (RESTRICT)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Family id={self.id} name='{self.name}'>"


class FamilyMember(Base):
    """FamilyMembers entity: Associates People with Family networks.
    
    A single Person record can belong to multiple families simultaneously.
    Duplicate memberships within the same family are forbidden via UNIQUE(family_id, person_id).
    """
    __tablename__ = "family_members"
    __table_args__ = (
        UniqueConstraint("family_id", "person_id", name="uq_family_members_family_person"),
        CheckConstraint(
            f"role IN {ALLOWED_FAMILY_ROLES}",
            name="ck_family_members_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Delete of person is restricted to protect family records integrity
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    joined_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<FamilyMember family_id={self.family_id} person_id={self.person_id} role={self.role}>"
