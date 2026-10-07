import re

with open("frontend/src/pages/People/PeoplePage.tsx", "r") as f:
    content = f.read()
content = content.replace("import { familiesApi } from '../../api/families';\n", "")
content = content.replace("import { relationshipsApi } from '../../api/relationships';\n", "")
with open("frontend/src/pages/People/PeoplePage.tsx", "w") as f:
    f.write(content)

with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "r") as f:
    content = f.read()
content = content.replace("import { familiesApi } from '../../api/families';\n", "")
content = content.replace("import { relationshipsApi } from '../../api/relationships';\n", "")
content = content.replace("loadGraph();", "initialize();")
with open("frontend/src/pages/Tree/FamilyTreePage.tsx", "w") as f:
    f.write(content)

