import re
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

content = content.replace("import { profileApi } from '../../api/profile';\n", "")
content = content.replace("const { user, profile } = useAuth() as any;", "const { user } = useAuth();")
content = content.replace("const [myPersonId, setMyPersonId] = useState<string | null>(null);", "")
content = content.replace("currentPersonId={myPersonId || undefined}", "currentPersonId={undefined}")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
