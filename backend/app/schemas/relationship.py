from uuid import UUID
from datetime import datetime, date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, model_validator

RelationshipType = Literal[
    "parent",
    "child",
    "spouse",
    "divorced_spouse",
    "sibling",
    "guardian",
]


class RelationshipBase(BaseModel):
    person_a_id: UUID
    person_b_id: UUID
    relationship_type: RelationshipType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = True

    @model_validator(mode="after")
    def check_not_self_relationship(self) -> "RelationshipBase":
        if self.person_a_id == self.person_b_id:
            raise ValueError("person_a_id cannot equal person_b_id (self-relationships are not allowed)")
        return self


class RelationshipCreate(RelationshipBase):
    pass


class RelationshipUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None


class RelationshipResponse(RelationshipBase):
    id: UUID
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
