import os

with open('backend/app/api/v1/invitations.py', 'r') as f:
    code = f.read()

# Replace both accept routes with a combined one
import re
new_code = re.sub(
    r'@router\.post\(\n\s+"/{token}/accept".*?def accept_invitation_by_id.*?\n',
    """@router.post(
    "/{identifier}/accept",
    response_model=PersonClaimResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Invitation",
)
def accept_invitation_combined(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PersonClaimResponse:
    service = PersonClaimService(db)
    try:
        inv_id = uuid.UUID(identifier)
        return service.accept_invitation_by_id(user_id=current_user.id, invitation_id=inv_id)
    except ValueError:
        return service.accept_invitation(user_id=current_user.id, raw_token=identifier)
""",
    code,
    flags=re.DOTALL
)

with open('backend/app/api/v1/invitations.py', 'w') as f:
    f.write(new_code)
