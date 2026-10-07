with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace(
    "import { MemoryDetailPage } from './pages/Memories/MemoryDetailPage';", 
    "import { MemoryDetailPage } from './pages/Memories/MemoryDetailPage';\nimport { MemoryCreatePage } from './pages/Memories/MemoryCreatePage';"
)

content = content.replace(
    "<Route path=\"memories\" element={<MemoriesPage />} />",
    "<Route path=\"memories\" element={<MemoriesPage />} />\n          <Route path=\"memories/new\" element={<MemoryCreatePage />} />"
)

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
