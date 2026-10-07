import re

with open("app/services/person_claim_service.py", "r") as f:
    content = f.read()

# Add accept_invitation_by_id
new_method = """
    def accept_invitation_by_id(self, user_id: uuid.UUID, invitation_id: uuid.UUID) -> PersonClaimResponse:
        \"\"\"Atomically validate and accept an invitation by ID.\"\"\"
        
        stmt = select(Invitation).where(Invitation.id == invitation_id)
        invitation = self.db.execute(stmt).scalar_one_or_none()
        if not invitation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found or invalid.")

        user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()

        if invitation.invited_by_user_id != user_id and (not invitation.invited_email or invitation.invited_email.lower() != user.email.lower()):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to accept this invitation.")

        if invitation.status == "accepted":
            if invitation.person.claimed_by_user_id == user_id:
                return PersonClaimResponse(person=SafePersonSummary.model_validate(invitation.person), claimed=True)
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
            person=SafePersonSummary.model_validate(person),
            claimed=True
        )
"""

content = content.replace("    def list_invitations", new_method + "\n    def list_invitations")

with open("app/services/person_claim_service.py", "w") as f:
    f.write(content)
