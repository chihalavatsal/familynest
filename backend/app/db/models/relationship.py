import uuid
from datetime import datetime, date, timezone
from typing import Optional
from sqlalchemy import String, Boolean, Date, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.models.base import Base

ALLOWED_RELATIONSHIP_TYPES = (
    'parent',
    'child',
    'spouse',
    'divorced_spouse',
    'sibling',
    'guardian',
)


class Relationship(Base):
    """Relationships entity: Stores fundamental family bonds and historical ties.
    
    CRITICAL ARCHITECTURE RULES:
    1. Only fundamental relationships are stored (parent, child, spouse, divorced_spouse, sibling, guardian).
       Derived relationships (uncle, aunt, cousin, grandparent) are calculated dynamically.
    2. Historical records are preserved non-destructively:
       - start_date, end_date, and is_current denote status over time.
       - A divorced spouse record coexists alongside previous and subsequent marriages.
    3. Self-relationships are forbidden (person_a_id != person_b_id).
    4. ON DELETE RESTRICT on person foreign keys protects ancestral and living family records.
    """
    __tablename__ = "relationships"
    __table_args__ = (
        CheckConstraint(
            "person_a_id != person_b_id",
            name="ck_relationships_no_self_relationship",
        ),
        CheckConstraint(
            f"relationship_type IN {ALLOWED_RELATIONSHIP_TYPES}",
            name="ck_relationships_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    person_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    person_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("people.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
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
        return f"<Relationship id={self.id} {self.person_a_id} -({self.relationship_type})-> {self.person_b_id} current={self.is_current}>"
