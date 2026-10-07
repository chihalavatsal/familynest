with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "r") as f:
    c = f.read()

c = c.replace("import { Button } from '../../components/ui/Button';\n", "")
c = c.replace("const { user } = useAuth();", "")
c = c.replace("if (f.role === 'owner' || f.role === 'admin') {", "if (true) {")
c = c.replace("{families.filter(f => f.role === 'owner' || f.role === 'admin').map(fam => {", "{families.map(fam => {")

with open("frontend/src/pages/Privacy/PrivacyPage.tsx", "w") as f:
    f.write(c)

with open("frontend/src/api/memories.ts", "r") as f:
    m = f.read()
m = m.replace(
    "create: (data: { family_id: string; title: string; body: string; memory_date?: string }) => api.post<MemoryResponse>('/memories', data),",
    "create: (data: { family_id: string; title: string; body: string; memory_date?: string; visibility?: string }) => api.post<MemoryResponse>('/memories', data),"
)
with open("frontend/src/api/memories.ts", "w") as f:
    f.write(m)
