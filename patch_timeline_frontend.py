with open('frontend/src/components/people/PersonTimeline.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'timelineApi.getTimeline(personId).then(setEvents)',
    'timelineApi.getTimeline(personId).then(res => { console.log("TIMELINE RES:", res); setEvents(res); })'
)

with open('frontend/src/components/people/PersonTimeline.tsx', 'w') as f:
    f.write(content)
