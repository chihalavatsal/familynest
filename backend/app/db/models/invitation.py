import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base

ALLOWED_INVITATION_STATUSES = ('pending', 'accepted', 'expired', 'cancelled')


class Invitation(Base):
    """Invitations entity: Tracks family network & account claim invitations.
    
    Allowed statuses: pending, accepted, expired, cancelled.
    Database check constraint enforces valid statuses.
    """
    __tablename__ = "invitations"
    __table_args__ = (
        CheckConstraint(
            f"status IN {ALLOWED_INVITATION_STATUSES}",
            name="ck_invitations_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    family_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("families.id", ondelete="SET NULL"),
        nullable=True,
    )
    person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invited_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invited_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    invited_phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    invitation_token: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Invitation id={self.id} person_id={self.person_id} status={self.status}>"
