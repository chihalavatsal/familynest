"""Relationship Repository — Phase 5.

Data access layer for canonical relationship graph records.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import Session

from app.db.models.relationship import Relationship
from app.db.models.person import Person
from app.schemas.relationship import SYMMETRIC_RELATIONSHIPS


MAX_PAGE_SIZE = 100


class RelationshipRepository:
    """Data access layer for Relationship entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_relationship(
        self,
        *,
        person_a_id: uuid.UUID,
        person_b_id: uuid.UUID,
        relationship_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        is_current: bool = True,
        created_by_user_id: uuid.UUID,
    ) -> Relationship:
        """Insert a new Relationship row. Caller must flush/commit."""
        rel = Relationship(
            person_a_id=person_a_id,
            person_b_id=person_b_id,
            relationship_type=relationship_type,
            start_date=start_date,
            end_date=end_date,
            is_current=is_current,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(rel)
        self.db.flush()
        return rel

    def get_by_id(self, relationship_id: uuid.UUID) -> Optional[Relationship]:
        """Fetch a Relationship by primary key."""
        stmt = select(Relationship).where(Relationship.id == relationship_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_duplicate(
        self,
        *,
        person_a_id: uuid.UUID,
        person_b_id: uuid.UUID,
        relationship_type: str,
        is_current: bool,
    ) -> Optional[Relationship]:
        """Find an existing logical relationship matching these criteria.
        
        If symmetric, checks both A->B and B->A.
        """
        is_sym = relationship_type in SYMMETRIC_RELATIONSHIPS
        
        if is_sym:
            match_cond = or_(
                and_(Relationship.person_a_id == person_a_id, Relationship.person_b_id == person_b_id),
                and_(Relationship.person_a_id == person_b_id, Relationship.person_b_id == person_a_id),
            )
        else:
            match_cond = and_(
                Relationship.person_a_id == person_a_id,
                Relationship.person_b_id == person_b_id,
            )
            
        stmt = select(Relationship).where(
            match_cond,
            Relationship.relationship_type == relationship_type,
            Relationship.is_current == is_current,
        )
        return self.db.execute(stmt).scalars().first()

    def list_relationships(
        self,
        *,
        allowed_person_ids: set[uuid.UUID],
        filter_person_id: Optional[uuid.UUID] = None,
        filter_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Relationship], int]:
        """Return paginated relationships.
        
        Only returns relationships where AT LEAST ONE person is in `allowed_person_ids`.
        (This satisfies "accessible through a Family the current User belongs to").
        """
        page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
        page = max(page, 1)

        # Base access condition: User must have access to either A or B
        access_cond = or_(
            Relationship.person_a_id.in_(allowed_person_ids),
            Relationship.person_b_id.in_(allowed_person_ids),
        )

        conditions = [access_cond]

        # Specific filters
        if filter_person_id:
            conditions.append(
                or_(
                    Relationship.person_a_id == filter_person_id,
                    Relationship.person_b_id == filter_person_id,
                )
            )
        if filter_type:
            conditions.append(Relationship.relationship_type == filter_type)

        combined = and_(*conditions) if conditions else True

        count_stmt = select(func.count()).select_from(Relationship).where(combined)
        total: int = self.db.execute(count_stmt).scalar_one()

        data_stmt = (
            select(Relationship)
            .where(combined)
            .order_by(Relationship.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.execute(data_stmt).scalars().all())
        return items, total

    def update_relationship(self, rel: Relationship, *, update_data: dict) -> Relationship:
        """Apply partial update fields. Caller must commit."""
        for field, value in update_data.items():
            setattr(rel, field, value)
        rel.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        return rel

    def delete_relationship(self, rel: Relationship) -> None:
        """Delete a Relationship row."""
        self.db.delete(rel)
        self.db.flush()
