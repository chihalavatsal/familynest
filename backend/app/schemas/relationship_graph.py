"""Relationship Graph Schemas — Phase 6.

Pydantic schemas for the read-only relationship graph engine.
"""
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


from app.schemas.person import SafePersonSummary

class SafePersonSummary(BaseModel):
    """A safe summary of a Person node in the graph."""
    id: UUID
    first_name: str
    last_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class RelationshipPathNode(BaseModel):
    """A single step in a relationship path."""
    person: SafePersonSummary
    relationship: str  # The edge label from the previous node to this node


class RelationshipPath(BaseModel):
    """A complete path between two people."""
    path: List[RelationshipPathNode]
    distance: int


class KinshipResult(BaseModel):
    """The result of a kinship query like 'how am I related?'"""
    source_person: SafePersonSummary
    target_person: SafePersonSummary
    relationship: Optional[str] = None
    distance: int
    path: List[RelationshipPathNode]


class RelatedPersonItem(BaseModel):
    """A related person (e.g. an ancestor or descendant) and their distance."""
    person: SafePersonSummary
    relationship: Optional[str] = None
    distance: int
    path: List[RelationshipPathNode]


class RelatedPersonListResponse(BaseModel):
    """A list of related people."""
    items: List[RelatedPersonItem]
    total: int
