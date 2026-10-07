import re

# Fix profileApi
with open("frontend/src/api/profile.ts", "r") as f:
    content = f.read()

content = content.replace("  updatePerson: (data: PersonProfileUpdate) =>", "  completeOnboarding: (data: any) => api.post<import('../types').PersonListItem>('/profile/onboarding', data),\n\n  updatePerson: (data: PersonProfileUpdate) =>")

with open("frontend/src/api/profile.ts", "w") as f:
    f.write(content)

# Fix OnboardingPrompt
with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "r") as f:
    content = f.read()

content = content.replace("await invitationsApi.listMyInvitations();", "await invitationsApi.list('received');")

with open("frontend/src/pages/Dashboard/OnboardingPrompt.tsx", "w") as f:
    f.write(content)

# Fix FamilyDetailPage.tsx redundant myRole and myPersonId error
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

# I see myRole declared twice. Let's remove the duplicate block.
content = re.sub(r'const \[myRole, setMyRole\] = useState<FamilyRole \| null>\(null\);\n  const \[myRole, setMyRole\] = useState<FamilyRole \| null>\(null\);\n  const \[myPersonId, setMyPersonId\] = useState<string \| null>\(null\);', 'const [myRole, setMyRole] = useState<FamilyRole | null>(null);\n  const [myPersonId, setMyPersonId] = useState<string | null>(null);', content, flags=re.MULTILINE)

# Just in case my regex didn't catch it:
lines = content.split('\n')
new_lines = []
for i, l in enumerate(lines):
    if l.strip() == "const [myRole, setMyRole] = useState<FamilyRole | null>(null);" and i > 0 and lines[i-1].strip() == l.strip():
        continue
    new_lines.append(l)

content = '\n'.join(new_lines)
content = content.replace("currentPersonId={myPersonId}", "currentPersonId={myPersonId || undefined}")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)

