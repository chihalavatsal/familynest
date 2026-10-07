import re

with open('frontend/src/components/profile/ProfileCompletenessBar.tsx', 'r') as f:
    content = f.read()

# Change export function ProfileCompletenessBar() { to accept a refresh trigger
content = content.replace(
    'export function ProfileCompletenessBar() {',
    'export function ProfileCompletenessBar({ refreshTrigger }: { refreshTrigger?: number }) {'
)

# Change useEffect dependency array from [] to [refreshTrigger]
content = content.replace(
    '  }, []);',
    '  }, [refreshTrigger]);'
)

with open('frontend/src/components/profile/ProfileCompletenessBar.tsx', 'w') as f:
    f.write(content)

with open('frontend/src/pages/Profile/ProfilePage.tsx', 'r') as f:
    page_content = f.read()

# Add a refreshTrigger state to ProfilePage
page_content = page_content.replace(
    '  const [isEditing, setIsEditing] = useState(false);',
    '  const [isEditing, setIsEditing] = useState(false);\n  const [refreshKey, setRefreshKey] = useState(0);'
)

# Trigger it on handleSave
page_content = page_content.replace(
    '      setIsEditing(false);',
    '      setIsEditing(false);\n      setRefreshKey(prev => prev + 1);'
)

# Pass it to the bar
page_content = page_content.replace(
    '<ProfileCompletenessBar />',
    '<ProfileCompletenessBar refreshTrigger={refreshKey} />'
)

with open('frontend/src/pages/Profile/ProfilePage.tsx', 'w') as f:
    f.write(page_content)
