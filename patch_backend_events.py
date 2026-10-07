import re

# Fix AudienceService
with open("backend/app/services/audience_service.py", "r") as f:
    content = f.read()

old_user_check = """        elif audience.type == AudienceType.USER:
            if not audience.user_id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="user_id is required for user audience")
            # Usually user audience is direct, but we might want to check if the creator is allowed.
            # For simplicity, if they can specify a user, they can send to them (or restrict to self/family members)
            # In FamilyNest, let's just return the user_id if valid.
            return {audience.user_id}"""

new_user_check = """        elif audience.type == AudienceType.USER:
            return {creator_user_id}"""
content = content.replace(old_user_check, new_user_check)
with open("backend/app/services/audience_service.py", "w") as f:
    f.write(content)

# Fix EventService
with open("backend/app/services/event_service.py", "r") as f:
    content = f.read()

old_target = """        # Create targets
        target = EventTarget(
            event_id=event.id,
            audience_type=data.audience.type,
            family_id=data.audience.family_id,
            user_id=data.audience.user_id
        )"""

new_target = """        # Create targets
        target_user_id = creator_user_id if data.audience.type == 'user' else data.audience.user_id
        target = EventTarget(
            event_id=event.id,
            audience_type=data.audience.type,
            family_id=data.audience.family_id,
            user_id=target_user_id
        )"""
content = content.replace(old_target, new_target)

old_activity = """        # Activity
        from app.db.models.activity import Activity
        act = Activity(
            activity_type=f"{data.event_type}.created",
            entity_type="event",
            entity_id=event.id,
            actor_user_id=creator_user_id,
            family_id=data.audience.family_id if data.audience.type == 'family' else None
        )
        self.db.add(act)"""

new_activity = """        # Activity
        if data.audience.type != 'user':
            from app.db.models.activity import Activity
            act = Activity(
                activity_type=f"{data.event_type}.created",
                entity_type="event",
                entity_id=event.id,
                actor_user_id=creator_user_id,
                family_id=data.audience.family_id if data.audience.type == 'family' else None
            )
            self.db.add(act)"""
content = content.replace(old_activity, new_activity)
with open("backend/app/services/event_service.py", "w") as f:
    f.write(content)

