import re

with open('frontend/src/pages/Profile/ProfilePage.tsx', 'r') as f:
    content = f.read()

if "import { PersonTimeline }" not in content:
    content = content.replace(
        "import { PersonUpcomingEvents } from '../../components/events/PersonUpcomingEvents';",
        "import { PersonUpcomingEvents } from '../../components/events/PersonUpcomingEvents';\nimport { PersonTimeline } from '../../components/people/PersonTimeline';"
    )

if "<PersonTimeline personId={profile.id} />" not in content:
    content = content.replace(
        "{profile && <PersonUpcomingEvents personId={profile.id} />}",
        "{profile && <PersonTimeline personId={profile.id} />}\n    {profile && <PersonUpcomingEvents personId={profile.id} />}"
    )

with open('frontend/src/pages/Profile/ProfilePage.tsx', 'w') as f:
    f.write(content)
