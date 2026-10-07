import re
# 1. Update profileApi
with open("frontend/src/api/profile.py" if False else "frontend/src/api/profile.ts", "r") as f:
    content = f.read()

if "completeOnboarding" not in content:
    content = content.replace("updatePerson(data: Partial", "completeOnboarding(data: any): Promise<import('../types').PersonListItem> {\n    return apiClient.post('/profile/onboarding', data);\n  },\n\n  updatePerson(data: Partial")
with open("frontend/src/api/profile.ts", "w") as f:
    f.write(content)

# 2. Update invitationsApi
with open("frontend/src/api/invitations.ts", "r") as f:
    content = f.read()

if "listMyInvitations" not in content:
    content = content.replace("accept(token: string)", "listMyInvitations(): Promise<import('../types').InvitationListResponse> {\n    return apiClient.get('/invitations'); // assuming /invitations lists mine\n  },\n\n  accept(token: string)")
with open("frontend/src/api/invitations.ts", "w") as f:
    f.write(content)
