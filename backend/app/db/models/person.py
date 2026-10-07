import uuid
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Text, Boolean, Date, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.models.base import Base

# Allowed profile status values
ALLOWED_PROFILE_STATUSES = ('unclaimed', 'invited', 'claimed', 'deceased')


class Person(Base):
    """People entity: Represents a real human being (identity).
    
    A Person can exist without a User account (unclaimed family member, child, deceased ancestor).
    When an account is created, a User can claim an existing Person record.
    
    Design Decision on claimed_by_user_id:
    A unique constraint is placed on `claimed_by_user_id`. In PostgreSQL, unique constraints
    permit multiple NULL values while enforcing that a non-null User ID can be linked to at most
    one Person record. This prevents a single user account from claiming multiple distinct
    canonical people in the family tree.
    """
    __tablename__ = "people"
    __table_args__ = (
        CheckConstraint(
            f"profile_status IN {ALLOWED_PROFILE_STATUSES}",
            name="ck_people_profile_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Nullable link to User account when claimed.
    # ondelete="SET NULL" protects historical family member records even if a user account is deleted.
    claimed_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    middle_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    nickname: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )
    date_of_death: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    death_place: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    birth_place: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    current_city: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    occupation: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    profile_photo_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    is_deceased: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_minor: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    profile_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unclaimed",
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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
        return f"<Person id={self.id} name='{self.first_name} {self.last_name or ''}' status={self.profile_status}>"
