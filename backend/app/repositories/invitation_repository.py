import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func

from app.db.models.invitation import Invitation


class InvitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, invitation: Invitation) -> Invitation:
        self.db.add(invitation)
        self.db.flush()
        return invitation

    def get_by_id(self, invitation_id: uuid.UUID) -> Optional[Invitation]:
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_token(self, token_hash: str) -> Optional[Invitation]:
        stmt = select(Invitation).where(Invitation.invitation_token == token_hash)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_invitations(
        self,
        user_id: uuid.UUID,
        user_email: Optional[str] = None,
        direction: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Invitation], int]:
        """List invitations. 'direction' can be 'sent' or 'received'."""
        filters = []
        
        if direction == 'sent':
            filters.append(Invitation.invited_by_user_id == user_id)
        elif direction == 'received':
            if user_email:
                filters.append(func.lower(Invitation.invited_email) == user_email.lower())
            else:
                return [], 0 # No email means no received invitations
        else:
            # Both
            or_conds = [Invitation.invited_by_user_id == user_id]
            if user_email:
                or_conds.append(func.lower(Invitation.invited_email) == user_email.lower())
            filters.append(or_(*or_conds))

        if status:
            filters.append(Invitation.status == status)

        stmt = select(Invitation).where(and_(*filters)).order_by(Invitation.created_at.desc())
        items = self.db.execute(stmt).scalars().all()
        return list(items), len(items)

    def count_pending_for_person(self, person_id: uuid.UUID, type_: str) -> int:
        stmt = select(func.count()).select_from(Invitation).where(
            and_(
                Invitation.person_id == person_id,
                Invitation.status == "pending",
                Invitation.invitation_type == type_
            )
        )
        return self.db.execute(stmt).scalar_one()

    def invalidate_pending_for_person(self, person_id: uuid.UUID, type_: str, exclude_id: Optional[uuid.UUID] = None) -> None:
        """Mark other pending invitations for this person as cancelled."""
        conditions = [
            Invitation.person_id == person_id,
            Invitation.status == "pending",
            Invitation.invitation_type == type_
        ]
        if exclude_id:
            conditions.append(Invitation.id != exclude_id)
            
        stmt = select(Invitation).where(and_(*conditions))
        for inv in self.db.execute(stmt).scalars().all():
            inv.status = "cancelled"
        self.db.flush()
