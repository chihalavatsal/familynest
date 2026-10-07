with open("backend/app/services/event_service.py", "r") as f:
    content = f.read()

old_update = """            else:
                targets = [EventTarget(event_id=event.id, audience_type=data.audience.type, family_id=data.audience.family_id, user_id=data.audience.user_id)]"""

new_update = """            else:
                target_user_id = user_id if data.audience.type == 'user' else data.audience.user_id
                targets = [EventTarget(event_id=event.id, audience_type=data.audience.type, family_id=data.audience.family_id, user_id=target_user_id)]"""

content = content.replace(old_update, new_update)

with open("backend/app/services/event_service.py", "w") as f:
    f.write(content)
