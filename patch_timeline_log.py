with open('backend/app/services/timeline_service.py', 'r') as f:
    content = f.read()

content = content.replace(
    'return events',
    'print(f"DEBUG TIMELINE EVENTS: {events}", flush=True)\n        return events'
)

with open('backend/app/services/timeline_service.py', 'w') as f:
    f.write(content)
