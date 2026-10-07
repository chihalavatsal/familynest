"""Relationship Schemas — Phase 5.

Schemas for managing the canonical relationship graph.
"""
from uuid import UUID
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, model_validator, Field

RelationshipType = Literal[
    "parent",
    "child",
    "spouse",
    "divorced_spouse",
    "sibling",
    "guardian",
]

SYMMETRIC_RELATIONSHIPS = {"spouse", "divorced_spouse", "sibling"}


class RelationshipCreate(BaseModel):
    """Fields a client may supply when creating a Relationship."""
    person_a_id: UUID
    person_b_id: UUID
    relationship_type: RelationshipType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = True

    @model_validator(mode="after")
    def validate_dates_and_self(self) -> "RelationshipCreate":
        if self.person_a_id == self.person_b_id:
            raise ValueError("person_a_id cannot equal person_b_id (no self-relationships)")
        
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be before start_date")
        
        return self


class RelationshipUpdate(BaseModel):
    """Fields a client may supply for a partial update of a Relationship.
    
    Note: person_a, person_b, and relationship_type are NOT editable via PATCH.
    To change identity/type, delete and recreate the relationship.
    """
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    
    # We allow explicit nullification of dates
    # But since Pydantic V2 Optional doesn't natively distinguish between omitted and None,
    # we'll do standard partial update in the service layer using exclude_unset.
    
    @model_validator(mode="after")
    def validate_dates(self) -> "RelationshipUpdate":
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValueError("end_date cannot be before start_date")
        return self


class PersonListItem(BaseModel):
    """Summary of a person attached to a relationship."""
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RelationshipResponse(BaseModel):
    """Full detail representation of a Relationship."""
    id: UUID
    person_a_id: UUID
    person_b_id: UUID
    relationship_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Optional nested summaries
    person_a: Optional[PersonListItem] = None
    person_b: Optional[PersonListItem] = None

    model_config = ConfigDict(from_attributes=True)


class RelationshipListItem(BaseModel):
    """Summary representation for lists."""
    id: UUID
    person_a_id: UUID
    person_b_id: UUID
    relationship_type: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool
    created_at: datetime
    updated_at: datetime
    
    person_a: Optional[PersonListItem] = None
    person_b: Optional[PersonListItem] = None

    model_config = ConfigDict(from_attributes=True)


class RelationshipListResponse(BaseModel):
    items: list[RelationshipListItem]
    page: int
    page_size: int
    total: int
