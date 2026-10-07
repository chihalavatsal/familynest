with open("frontend/src/App.tsx", "r") as f:
    content = f.read()

content = content.replace("import { ActivityPage } from './pages/Activity/ActivityPage';", "import { ActivityPage } from './pages/Activity/ActivityPage';\nimport { SearchResultsPage } from './pages/Search/SearchResultsPage';")
content = content.replace("<Route path=\"/activity\" element={<ActivityPage />} />", "<Route path=\"/activity\" element={<ActivityPage />} />\n                <Route path=\"/search\" element={<SearchResultsPage />} />")

with open("frontend/src/App.tsx", "w") as f:
    f.write(content)
