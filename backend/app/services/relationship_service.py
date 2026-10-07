"""Relationship Service — Phase 5.

Business logic and authorization for the Relationship API.
Maintains absolute boundary separation from Families (no merges, no auto-memberships).
"""
import uuid
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_

from app.db.models.user import User
from app.db.models.person import Person
from app.db.models.family import Family, FamilyMember
from app.db.models.relationship import Relationship
from app.db.models.audit_log import AuditLog
from app.repositories.relationship_repository import RelationshipRepository
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    RelationshipListItem,
    RelationshipListResponse,
    PersonListItem,
)


def _build_person_summary(person: Optional[Person]) -> Optional[PersonListItem]:
    if not person:
        return None
    return PersonListItem(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
    )


def _build_response(rel: Relationship, person_a: Person, person_b: Person) -> RelationshipResponse:
    return RelationshipResponse(
        id=rel.id,
        person_a_id=rel.person_a_id,
        person_b_id=rel.person_b_id,
        relationship_type=rel.relationship_type,
        start_date=rel.start_date,
        end_date=rel.end_date,
        is_current=rel.is_current,
        created_by_user_id=rel.created_by_user_id,
        created_at=rel.created_at,
        updated_at=rel.updated_at,
        person_a=_build_person_summary(person_a),
        person_b=_build_person_summary(person_b),
    )


class RelationshipService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = RelationshipRepository(db)

    def _get_allowed_person_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        """Resolve all Person IDs the current user has legitimate access to.
        
        Access is granted if:
        1. User created the Person.
        2. User claimed the Person.
        3. Person is a member of a Family that the User created.
        4. Person is a member of a Family that the User's claimed Person is a member of.
        """
        # 1 & 2: Direct control
        direct_stmt = select(Person.id).where(
            or_(
                Person.created_by_user_id == user_id,
                Person.claimed_by_user_id == user_id,
            )
        )
        direct_ids = {row[0] for row in self.db.execute(direct_stmt).all()}

        # 3 & 4: Network access
        claimed_person_stmt = select(Person.id).where(Person.claimed_by_user_id == user_id)
        
        accessible_families_stmt = select(Family.id).outerjoin(
            FamilyMember, Family.id == FamilyMember.family_id
        ).where(
            or_(
                Family.created_by_user_id == user_id,
                FamilyMember.person_id.in_(claimed_person_stmt),
            )
        )
        
        network_stmt = select(FamilyMember.person_id).where(
            FamilyMember.family_id.in_(accessible_families_stmt)
        )
        network_ids = {row[0] for row in self.db.execute(network_stmt).all()}
        
        return direct_ids.union(network_ids)

    def _require_access_to_people(self, person_ids: list[uuid.UUID], allowed_ids: set[uuid.UUID]) -> None:
        """Verify the user has access to ALL provided person IDs."""
        for pid in person_ids:
            if pid not in allowed_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Person not found or access denied.",
                )

    def _get_people_or_404(self, person_a_id: uuid.UUID, person_b_id: uuid.UUID) -> tuple[Person, Person]:
        """Fetch both Person records simultaneously."""
        stmt = select(Person).where(Person.id.in_([person_a_id, person_b_id]))
        people = {p.id: p for p in self.db.execute(stmt).scalars().all()}
        
        if person_a_id not in people or person_b_id not in people:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both Person records do not exist.",
            )
        return people[person_a_id], people[person_b_id]

    def _write_audit(
        self,
        *,
        actor_user_id: uuid.UUID,
        action: str,
        entity_id: uuid.UUID,
        metadata: dict,
    ) -> None:
        audit = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type="relationship",
            entity_id=entity_id,
            metadata_=metadata,
        )
        self.db.add(audit)

    # ------------------------------------------------------------------
    # CRUD Operations
    # ------------------------------------------------------------------

    def create_relationship(self, *, data: RelationshipCreate, current_user: User) -> RelationshipResponse:
        """Create a new Relationship between two People."""
        allowed_ids = self._get_allowed_person_ids(current_user.id)
        self._require_access_to_people([data.person_a_id, data.person_b_id], allowed_ids)
        
        person_a, person_b = self._get_people_or_404(data.person_a_id, data.person_b_id)
        
        # Prevent logical duplicates
        existing = self.repo.find_duplicate(
            person_a_id=data.person_a_id,
            person_b_id=data.person_b_id,
            relationship_type=data.relationship_type,
            is_current=data.is_current,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A matching logical relationship already exists.",
            )
            
        try:
            rel = self.repo.create_relationship(
                person_a_id=data.person_a_id,
                person_b_id=data.person_b_id,
                relationship_type=data.relationship_type,
                start_date=data.start_date,
                end_date=data.end_date,
                is_current=data.is_current,
                created_by_user_id=current_user.id,
            )
            
            self._write_audit(
                actor_user_id=current_user.id,
                action="relationship.create",
                entity_id=rel.id,
                metadata={
                    "type": rel.relationship_type,
                    "person_a_id": str(rel.person_a_id),
                    "person_b_id": str(rel.person_b_id),
                }
            )
            self.db.commit()
            self.db.refresh(rel)
        except Exception:
            self.db.rollback()
            raise
            
        return _build_response(rel, person_a, person_b)

    def get_relationship(self, *, relationship_id: uuid.UUID, current_user: User) -> RelationshipResponse:
        """Retrieve a specific Relationship."""
        rel = self.repo.get_by_id(relationship_id)
        if not rel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
            
        allowed_ids = self._get_allowed_person_ids(current_user.id)
        
        # The user must have access to at least ONE of the people in the relationship to see it
        if rel.person_a_id not in allowed_ids and rel.person_b_id not in allowed_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
            
        person_a, person_b = self._get_people_or_404(rel.person_a_id, rel.person_b_id)
        return _build_response(rel, person_a, person_b)

    def list_relationships(
        self,
        *,
        current_user: User,
        person_id: Optional[uuid.UUID] = None,
        relationship_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> RelationshipListResponse:
        """List accessible relationships."""
        allowed_ids = self._get_allowed_person_ids(current_user.id)
        
        if person_id and person_id not in allowed_ids:
            # Filtering on a person you don't have access to -> return 0 results (privacy-preserving)
            return RelationshipListResponse(items=[], page=page, page_size=page_size, total=0)
            
        rels, total = self.repo.list_relationships(
            allowed_person_ids=allowed_ids,
            filter_person_id=person_id,
            filter_type=relationship_type,
            page=page,
            page_size=page_size,
        )
        
        # Batch fetch people for performance
        needed_person_ids = set()
        for r in rels:
            needed_person_ids.add(r.person_a_id)
            needed_person_ids.add(r.person_b_id)
            
        people_dict = {}
        if needed_person_ids:
            stmt = select(Person).where(Person.id.in_(needed_person_ids))
            people_dict = {p.id: p for p in self.db.execute(stmt).scalars().all()}
            
        items = []
        for r in rels:
            pa = people_dict.get(r.person_a_id)
            pb = people_dict.get(r.person_b_id)
            items.append(
                RelationshipListItem(
                    id=r.id,
                    person_a_id=r.person_a_id,
                    person_b_id=r.person_b_id,
                    relationship_type=r.relationship_type,
                    start_date=r.start_date,
                    end_date=r.end_date,
                    is_current=r.is_current,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                    person_a=_build_person_summary(pa),
                    person_b=_build_person_summary(pb),
                )
            )
            
        return RelationshipListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def update_relationship(
        self, *, relationship_id: uuid.UUID, data: RelationshipUpdate, current_user: User
    ) -> RelationshipResponse:
        """Patch a Relationship (dates and current status only)."""
        rel = self.repo.get_by_id(relationship_id)
        if not rel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
            
        allowed_ids = self._get_allowed_person_ids(current_user.id)
        
        # Must have access to both to modify it, or at least one?
        # Standard: you must have access to BOTH people to modify their relationship.
        if rel.person_a_id not in allowed_ids or rel.person_b_id not in allowed_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient access to modify this relationship")

        update_dict = data.model_dump(exclude_unset=True)
        if not update_dict:
            person_a, person_b = self._get_people_or_404(rel.person_a_id, rel.person_b_id)
            return _build_response(rel, person_a, person_b)
            
        try:
            rel = self.repo.update_relationship(rel, update_data=update_dict)
            self._write_audit(
                actor_user_id=current_user.id,
                action="relationship.update",
                entity_id=rel.id,
                metadata={"changed_fields": list(update_dict.keys())}
            )
            self.db.commit()
            self.db.refresh(rel)
        except Exception:
            self.db.rollback()
            raise
            
        person_a, person_b = self._get_people_or_404(rel.person_a_id, rel.person_b_id)
        return _build_response(rel, person_a, person_b)

    def delete_relationship(self, *, relationship_id: uuid.UUID, current_user: User) -> None:
        """Hard delete a Relationship."""
        rel = self.repo.get_by_id(relationship_id)
        if not rel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
            
        allowed_ids = self._get_allowed_person_ids(current_user.id)
        if rel.person_a_id not in allowed_ids or rel.person_b_id not in allowed_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient access to delete this relationship")
            
        try:
            self._write_audit(
                actor_user_id=current_user.id,
                action="relationship.delete",
                entity_id=rel.id,
                metadata={
                    "type": rel.relationship_type,
                    "person_a_id": str(rel.person_a_id),
                    "person_b_id": str(rel.person_b_id),
                }
            )
            self.repo.delete_relationship(rel)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
