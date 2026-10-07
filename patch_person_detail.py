import re

with open('frontend/src/pages/People/PersonDetailPage.tsx', 'r') as f:
    content = f.read()

# Add import
content = content.replace(
    "import { PersonConnections } from '../../components/people/PersonConnections';",
    "import { PersonConnections } from '../../components/people/PersonConnections';\nimport { PersonTimeline } from '../../components/people/PersonTimeline';"
)

# Insert component before Events
content = content.replace(
    "{/* Events */}",
    "{/* Timeline */}\n      <PersonTimeline personId={p.id} />\n\n      {/* Events */}"
)

with open('frontend/src/pages/People/PersonDetailPage.tsx', 'w') as f:
    f.write(content)
