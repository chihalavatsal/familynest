import re

with open("app/api/v1/invitations.py", "r") as f:
    content = f.read()

new_endpoint = """
@router.post(
    "/{invitation_id}/accept",
    response_model=PersonClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Invitation by ID",
)
def accept_invitation_by_id(
    invitation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonClaimResponse:
    service = PersonClaimService(db)
    return service.accept_invitation_by_id(user_id=current_user.id, invitation_id=invitation_id)
"""

content = content + new_endpoint

with open("app/api/v1/invitations.py", "w") as f:
    f.write(content)
