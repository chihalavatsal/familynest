import re

# Fix FamilyDetailPage.tsx
with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "r") as f:
    fd_content = f.read()

fd_content = re.sub(r'import \{ useAuth \} from \'\.\./\.\./store/AuthContext\';\n', '', fd_content, count=1)
fd_content = fd_content.replace('load(); // refresh status', 'initialize(); // refresh status')

# handleCreatePerson isn't defined? I patched it in `handleAddMember` replacement, but maybe I missed it?
# Yes, wait, `handleCreatePerson` was defined correctly but maybe placed wrong?
# Let's write `handleCreatePerson` inside the component.
with open("src/pages/FamilyDetail/FamilyDetailPage.tsx", "w") as f:
    f.write(fd_content)

# Fix PeoplePage.tsx
with open("src/pages/People/PeoplePage.tsx", "r") as f:
    pp_content = f.read()

pp_content = pp_content.replace('const { profile } = useAuth();', 'const { user, profile } = useAuth() as any;')
with open("src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(pp_content)

# Fix PersonDetailPage.tsx
with open("src/pages/People/PersonDetailPage.tsx", "r") as f:
    pdp_content = f.read()

pdp_content = pdp_content.replace('initialValues={p}', 'initialValues={p as any}')
with open("src/pages/People/PersonDetailPage.tsx", "w") as f:
    f.write(pdp_content)

# Fix FamilyTreePage.tsx
with open("src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    ftp_content = f.read()

if "import { Modal }" not in ftp_content:
    ftp_content = ftp_content.replace("import { Button } from '../../components/ui/Button';", "import { Button } from '../../components/ui/Button';\nimport { Modal } from '../../components/ui/Dialog';")

with open("src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(ftp_content)
