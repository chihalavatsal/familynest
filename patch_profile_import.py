with open('frontend/src/pages/Profile/ProfilePage.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'import { PersonUpcomingEvents } from "../../components/events/PersonUpcomingEvents";',
    'import { PersonUpcomingEvents } from "../../components/events/PersonUpcomingEvents";\nimport { PersonTimeline } from "../../components/people/PersonTimeline";'
)

with open('frontend/src/pages/Profile/ProfilePage.tsx', 'w') as f:
    f.write(content)
