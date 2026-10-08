import uuid
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.person import Person
from app.db.models.user import User
from app.db.models.audit_log import AuditLog
from app.db.models.invitation import Invitation
from app.services.relationship_service import RelationshipService
from app.repositories.invitation_repository import InvitationRepository
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationDetailResponse,
    InvitationListResponse,
    PersonClaimResponse,
    INVITATION_TYPE_CLAIM,
)
from app.schemas.person import PersonListItem
from app.services.email_service import email_service
from app.core.config import settings


class PersonClaimService:
    def __init__(self, db: Session):
        self.db = db
        self.rel_service = RelationshipService(db)
        self.inv_repo = InvitationRepository(db)

    def _require_accessible(self, person_id: uuid.UUID, user_id: uuid.UUID) -> Person:
        allowed = self.rel_service._get_allowed_person_ids(user_id)
        if person_id not in allowed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
        
        stmt = select(Person).where(Person.id == person_id)
        return self.db.execute(stmt).scalar_one()

    def _ensure_no_existing_claim(self, user_id: uuid.UUID):
        stmt = select(Person).where(Person.claimed_by_user_id == user_id)
        if self.db.execute(stmt).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already claimed a Person profile. A User account can only claim one Person."
            )

    def _ensure_claimable(self, person: Person):
        if person.is_deceased:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A deceased Person profile cannot be claimed."
            )
        if person.claimed_by_user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This person profile has already been claimed."
            )

    def claim_person(self, user_id: uuid.UUID, person_id: uuid.UUID) -> PersonClaimResponse:
        """Directly claim an accessible person."""
        # Validate accessibility
        person = self._require_accessible(person_id, user_id)
        
        # Invariants
        self._ensure_claimable(person)
        self._ensure_no_existing_claim(user_id)

        try:
            # Atomic update
            person.claimed_by_user_id = user_id
            person.profile_status = "claimed"
            person.updated_at = datetime.now(timezone.utc)

            # Invalidate any pending claim invitations for this person
            self.inv_repo.invalidate_pending_for_person(person_id, INVITATION_TYPE_CLAIM)

            # Audit
            audit = AuditLog(
                actor_user_id=user_id,
                action="person.claim",
                entity_type="person",
                entity_id=person.id,
                metadata_={"method": "direct"}
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(person)
        except Exception:
            self.db.rollback()
            raise

        return PersonClaimResponse(
            person=PersonListItem.model_validate(person),
            claimed=True
        )

    def create_invitation(
        self, user_id: uuid.UUID, person_id: uuid.UUID, data: InvitationCreate
    ) -> InvitationDetailResponse:
        """Create a secure invitation token for claiming."""
        person = self._require_accessible(person_id, user_id)
        self._ensure_claimable(person)

        # Generate secure random token
        raw_token = secrets.token_urlsafe(32)

        try:
            invitation = Invitation(
                person_id=person.id,
                invited_by_user_id=user_id,
                invited_email=data.invited_email.lower() if data.invited_email else None,
                invited_phone=data.invited_phone,
                invitation_type=data.invitation_type,
                invitation_token=raw_token,
                status="pending",
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            )
            self.db.add(invitation)

            audit = AuditLog(
                actor_user_id=user_id,
                action="invitation.create",
                entity_type="invitation",
                entity_id=invitation.id,
                metadata_={
                    "person_id": str(person.id),
                    "type": data.invitation_type
                }
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(invitation)
            
            # Send Email via Brevo
            if invitation.invited_email:
                inviter = self.db.query(User).filter(User.id == user_id).first()
                inviter_name = inviter.email.split('@')[0] if inviter else "Someone"
                
                # Fetch family name if available
                family_name = "your"
                if person.family_id:
                    from app.db.models.family import Family
                    family = self.db.query(Family).filter(Family.id == person.family_id).first()
                    if family:
                        family_name = family.name

                person_name = f"{person.first_name} {person.last_name or ''}".strip()
                
                email_service.send_invitation_email(
                    to_email=invitation.invited_email,
                    inviter_name=inviter_name,
                    person_name=person_name,
                    family_name=family_name,
                    frontend_url=settings.FRONTEND_URL
                )

        except Exception:
            self.db.rollback()
            raise

        resp = InvitationDetailResponse.model_validate(invitation)
        resp.invitation_token = raw_token  # ONLY returned during creation
        return resp

    def accept_invitation(self, user_id: uuid.UUID, raw_token: str) -> PersonClaimResponse:
        """Atomically validate and accept an invitation."""
        
        # Token lookup
        stmt = select(Invitation).where(Invitation.invitation_token == raw_token)
        invitation = self.db.execute(stmt).scalar_one_or_none()
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or invalid.")

        # Ensure we lock the person / invitation row appropriately if we want perfect concurrency
        # But we rely on the unique constraint for claimed_by_user_id.

        if invitation.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer valid.")

        if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
            try:
                invitation.status = "expired"
                audit = AuditLog(
                    actor_user_id=user_id,
                    action="invitation.expire",
                    entity_type="invitation",
                    entity_id=invitation.id,
                    metadata_={"person_id": str(invitation.person_id)}
                )
                self.db.add(audit)
                self.db.commit()
            except Exception:
                self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has expired.")

        # Email recipient check
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        if invitation.invited_email and invitation.invited_email.lower() != user.email.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This invitation was sent to a different email address.")

        person = self.db.execute(select(Person).where(Person.id == invitation.person_id)).scalar_one()
        self._ensure_claimable(person)
        self._ensure_no_existing_claim(user_id)

        try:
            # Atomic update
            person.claimed_by_user_id = user_id
            person.profile_status = "claimed"
            person.updated_at = datetime.now(timezone.utc)
            
            invitation.status = "accepted"

            # Invalidate others
            self.inv_repo.invalidate_pending_for_person(person.id, INVITATION_TYPE_CLAIM, exclude_id=invitation.id)

            audit_claim = AuditLog(
                actor_user_id=user_id,
                action="person.claim",
                entity_type="person",
                entity_id=person.id,
                metadata_={"method": "invitation", "invitation_id": str(invitation.id)}
            )
            audit_inv = AuditLog(
                actor_user_id=user_id,
                action="invitation.accept",
                entity_type="invitation",
                entity_id=invitation.id,
                metadata_={"person_id": str(person.id)}
            )
            self.db.add_all([audit_claim, audit_inv])
            self.db.commit()
            self.db.refresh(person)
        except Exception:
            self.db.rollback()
            raise

        return PersonClaimResponse(
            person=PersonListItem.model_validate(person),
            claimed=True
        )

    def cancel_invitation(self, user_id: uuid.UUID, invitation_id: uuid.UUID) -> InvitationResponse:
        invitation = self.inv_repo.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")
            
        # Auth check (only creator or someone with family rights. For now, creator)
        if invitation.invited_by_user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        if invitation.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending invitations can be cancelled.")

        try:
            invitation.status = "cancelled"
            audit = AuditLog(
                actor_user_id=user_id,
                action="invitation.cancel",
                entity_type="invitation",
                entity_id=invitation.id,
                metadata_={"person_id": str(invitation.person_id)}
            )
            self.db.add(audit)
            self.db.commit()
            self.db.refresh(invitation)
        except Exception:
            self.db.rollback()
            raise

        return InvitationResponse.model_validate(invitation)

    def get_invitation(self, user_id: uuid.UUID, invitation_id: uuid.UUID) -> InvitationResponse:
        invitation = self.inv_repo.get_by_id(invitation_id)
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")
            
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        
        # Can see if you sent it, or if you are the recipient email
        if invitation.invited_by_user_id != user_id and (not invitation.invited_email or invitation.invited_email.lower() != user.email.lower()):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found.")

        # Passive expiry check
        if invitation.status == "pending" and invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
            try:
                invitation.status = "expired"
                audit = AuditLog(
                    actor_user_id=user_id,
                    action="invitation.expire",
                    entity_type="invitation",
                    entity_id=invitation.id,
                    metadata_={"person_id": str(invitation.person_id)}
                )
                self.db.add(audit)
                self.db.commit()
                self.db.refresh(invitation)
            except Exception:
                self.db.rollback()

        return InvitationResponse.model_validate(invitation)


    def accept_invitation_by_id(self, user_id: uuid.UUID, invitation_id: uuid.UUID) -> PersonClaimResponse:
        """Atomically validate and accept an invitation by ID."""
        
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        invitation = self.db.execute(stmt).scalar_one_or_none()
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or invalid.")

        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()

        if invitation.invited_by_user_id != user_id and (not invitation.invited_email or invitation.invited_email.lower() != user.email.lower()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to accept this invitation.")

        if invitation.status == "accepted":
            if invitation.person.claimed_by_user_id == user_id:
                return PersonClaimResponse(person=PersonListItem.model_validate(invitation.person), claimed=True)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has already been accepted by another user.")

        if invitation.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is no longer valid.")

        if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
            try:
                invitation.status = "expired"
                audit = AuditLog(
                    actor_user_id=user_id,
                    action="invitation.expire",
                    entity_type="invitation",
                    entity_id=invitation.id,
                    metadata_={"person_id": str(invitation.person_id)}
                )
                self.db.add(audit)
                self.db.commit()
            except Exception:
                self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has expired.")

        # Accept
        person = invitation.person
        if person.is_deceased:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot claim a deceased person.")

        if person.claimed_by_user_id and person.claimed_by_user_id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Person is already claimed by another user.")

        person.claimed_by_user_id = user_id
        person.profile_status = "claimed"
        invitation.status = "accepted"

        # Cancel others
        stmt_others = select(Invitation).where(
            Invitation.person_id == person.id,
            Invitation.id != invitation.id,
            Invitation.status == "pending"
        )
        other_invites = self.db.execute(stmt_others).scalars().all()
        for oi in other_invites:
            oi.status = "cancelled"

        audit_accept = AuditLog(
            actor_user_id=user_id,
            action="invitation.accept",
            entity_type="invitation",
            entity_id=invitation.id,
            metadata_={"person_id": str(person.id)}
        )
        self.db.add(audit_accept)

        audit_claim = AuditLog(
            actor_user_id=user_id,
            action="person.claim",
            entity_type="person",
            entity_id=person.id,
            metadata_={"invitation_id": str(invitation.id)}
        )
        self.db.add(audit_claim)

        self.db.commit()
        self.db.refresh(person)

        return PersonClaimResponse(
            person=PersonListItem.model_validate(person),
            claimed=True
        )

    def list_invitations(self, user_id: uuid.UUID, direction: Optional[str] = None) -> InvitationListResponse:
        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
        items, total = self.inv_repo.list_invitations(user_id=user_id, user_email=user.email, direction=direction)
        
        return InvitationListResponse(
            items=[InvitationResponse.model_validate(i) for i in items],
            total=total
        )
