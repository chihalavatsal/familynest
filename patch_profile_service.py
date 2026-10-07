import re

with open("backend/app/services/profile_service.py", "r") as f:
    content = f.read()

# Add import
if "LifeEventsService" not in content:
    content = content.replace("from app.services.activity_service import ActivityService", "from app.services.activity_service import ActivityService\nfrom app.services.life_events_service import LifeEventsService")

# Inject life events
old_events = """        # Events
        events, _ = self.event_service.list_events(user_id, limit=5, upcoming=True)
        event_responses = [EventResponse.model_validate(e) for e in events]"""

new_events = """        # Events
        events, _ = self.event_service.list_events(user_id, limit=5, upcoming=True)
        event_responses = [EventResponse.model_validate(e) for e in events]
        
        # Life Events
        life_events = LifeEventsService(self.db).get_upcoming_events(user_id, days=30)
        event_responses.extend(life_events)
        
        # Sort combined events by date
        def get_sort_key(e: EventResponse):
            if e.start_datetime:
                return e.start_datetime.date()
            if e.start_date:
                return e.start_date
            return date.max
        event_responses.sort(key=get_sort_key)
        # Limit total upcoming to 10
        event_responses = event_responses[:10]"""

content = content.replace(old_events, new_events)

with open("backend/app/services/profile_service.py", "w") as f:
    f.write(content)
