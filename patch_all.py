import re

# 1. Fix App.tsx
with open("frontend/src/App.tsx", "r") as f:
    app_content = f.read()

routes_to_add = """<Route path="/activity" element={<ActivityPage />} />
                <Route path="/memories" element={<MemoriesPage />} />
                <Route path="/memories/new" element={<MemoryCreatePage />} />
                <Route path="/memories/:id" element={<MemoryDetailPage />} />"""

app_content = app_content.replace('<Route path="/activity" element={<ActivityPage />} />', routes_to_add)

with open("frontend/src/App.tsx", "w") as f:
    f.write(app_content)

# 2. Fix MemoriesPage.tsx
with open("frontend/src/pages/Memories/MemoriesPage.tsx", "r") as f:
    mem_content = f.read()

mem_content = mem_content.replace("const { currentFamilyId } = useAuth();", "const { currentFamily } = useAuth();\n  const currentFamilyId = currentFamily?.id;")
mem_content = mem_content.replace('role="button"\n              tabIndex={0}', 'tabIndex={0}')

with open("frontend/src/pages/Memories/MemoriesPage.tsx", "w") as f:
    f.write(mem_content)

# 3. Fix MemoryCreatePage.tsx
with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "r") as f:
    c_content = f.read()

c_content = c_content.replace("../../components/ui/useToast", "../../components/ui/Toast")
c_content = c_content.replace("const { currentFamilyId } = useAuth();", "const { currentFamily } = useAuth();\n  const currentFamilyId = currentFamily?.id;")
c_content = c_content.replace('variant="outline"', 'variant="secondary"')
c_content = c_content.replace('isLoading={isSubmitting}', 'loading={isSubmitting}')

with open("frontend/src/pages/Memories/MemoryCreatePage.tsx", "w") as f:
    f.write(c_content)

# 4. Fix MemoryDetailPage.tsx
with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "r") as f:
    d_content = f.read()

d_content = d_content.replace("../../components/ui/useToast", "../../components/ui/Toast")
d_content = d_content.replace("../../components/ui/ConfirmDialog", "../../components/ui/Dialog")
d_content = d_content.replace('variant="outline"', 'variant="secondary"')
d_content = d_content.replace('isLoading={isDeleting}', 'loading={isDeleting}')

with open("frontend/src/pages/Memories/MemoryDetailPage.tsx", "w") as f:
    f.write(d_content)

