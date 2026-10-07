with open('frontend/src/components/people/PersonTimeline.tsx', 'r') as f:
    content = f.read()

# Replace the catch to actually log the error
content = content.replace(
    ".catch(() => setEvents([]))",
    ".catch(err => { console.error('TIMELINE ERROR:', err); setEvents([]); })"
)

with open('frontend/src/components/people/PersonTimeline.tsx', 'w') as f:
    f.write(content)
