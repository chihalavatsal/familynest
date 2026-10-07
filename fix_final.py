with open("frontend/src/pages/Memories/MemoriesPage.tsx", "r") as f:
    c = f.read()
c = c.replace("import { useAuth } from '../../store/AuthContext';", "")
c = c.replace('tabIndex={0}', '')
with open("frontend/src/pages/Memories/MemoriesPage.tsx", "w") as f:
    f.write(c)

with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "r") as f:
    c = f.read()
c = c.replace("import { useAuth } from '../../store/AuthContext';", "")
c = c.replace("import { useState }", "import { useState, useEffect }")
with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "w") as f:
    f.write(c)

with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "r") as f:
    c = f.read()
c = c.replace("isDestructive\n", "")
with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "w") as f:
    f.write(c)

with open("frontend/src/components/navigation/Navigation.tsx", "r") as f:
    c = f.read()
c = c.replace("  BookOpen\n} from 'lucide-react';", "} from 'lucide-react';")
with open("frontend/src/components/navigation/Navigation.tsx", "w") as f:
    f.write(c)

