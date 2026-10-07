with open("src/pages/Dashboard/OnboardingPrompt.tsx", "r") as f:
    content = f.read()

content = content.replace("if (onComplete) onComplete();, setting profile and removing onboarding state", "if (onComplete) onComplete(); // setting profile and removing onboarding state")

with open("src/pages/Dashboard/OnboardingPrompt.tsx", "w") as f:
    f.write(content)

with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

content = content.replace("import { profileApi }\nimport { peopleApi } from", "import { profileApi } from '../../api/profile';\nimport { peopleApi } from")
content = content.replace("const [myPersonId, setMyPersonId] = useState<string | null>(null);<FamilyRole | null>(null);", "const [myRole, setMyRole] = useState<FamilyRole | null>(null);\n  const [myPersonId, setMyPersonId] = useState<string | null>(null);")

with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)

