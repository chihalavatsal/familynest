import re
with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    content = f.read()

# Add profileApi import
if "import { profileApi }" not in content:
    content = content.replace("import { peopleApi }", "import { profileApi }\nimport { peopleApi }")

# Add myPersonId state
if "const [myPersonId, setMyPersonId]" not in content:
    content = content.replace("const [myRole, setMyRole] = useState", "const [myRole, setMyRole] = useState<FamilyRole | null>(null);\n  const [myPersonId, setMyPersonId] = useState<string | null>(null);")

# Update loadFamily to fetch profile
load_family_patch = """
    try {
      if (!familyId) throw new Error('No family ID');
      const [famRes, memRes, profRes] = await Promise.all([
        familiesApi.get(familyId),
        familiesApi.listMembers(familyId),
        profileApi.getProfile().catch(() => null)
      ]);
      
      setFamily(famRes);
      setMembers(memRes.items);
      
      if (profRes && (profRes as any).person) {
        setMyPersonId((profRes as any).person.id);
      }
"""
content = re.sub(r'try \{\n\s*if \(\!familyId\).*?setMembers\(memRes\.items\);', load_family_patch, content, flags=re.DOTALL)

# Fix the references to `profile`
content = content.replace("(profile as any)?.person?.id", "myPersonId")
content = content.replace("(profile as any).person.id", "myPersonId")
content = content.replace("const { profile } = useAuth() as any;", "")

with open("frontend/src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(content)
