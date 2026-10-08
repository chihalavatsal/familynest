with open('backend/app/api/v1/invitations.py', 'r') as f:
    lines = f.readlines()

# Find the end of the combined function
target_idx = -1
for i, line in enumerate(lines):
    if "return service.accept_invitation(user_id=current_user.id, raw_token=identifier)" in line:
        target_idx = i
        break

if target_idx != -1:
    lines = lines[:target_idx + 1]
    with open('backend/app/api/v1/invitations.py', 'w') as f:
        f.writelines(lines)
