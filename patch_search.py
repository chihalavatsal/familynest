with open("backend/app/services/search_service.py", "r") as f:
    content = f.read()

old_event_search = """        # 5. Events
        if not type_filter or type_filter == 'event':
            # Event authorization: user must have access to the target family/members.
            # We filter by events targeting the allowed families.
            stmt = select(Event, Family.id, Family.name).join(
                EventTarget, EventTarget.event_id == Event.id
            ).join(
                Family, Family.id == EventTarget.family_id
            ).where(
                Family.id.in_(allowed_family_ids),
                Event.title.ilike(search_pattern)
            ).limit(limit)
            
            # Simple deduplication just in case
            seen_events = set()
            for ev, f_id, f_name in self.db.execute(stmt).all():
                if ev.id in seen_events: continue
                seen_events.add(ev.id)
                results.append(SearchResult(
                    id=ev.id,
                    type="event",
                    title=ev.title,
                    subtitle="Event",
                    family_id=f_id,
                    family_name=f_name,
                    route=f"/events/{ev.id}"
                ))"""

new_event_search = """        # 5. Events
        if not type_filter or type_filter == 'event':
            # Event authorization: user must have access to the target family/members OR user is target.
            
            # Find Family events
            stmt = select(Event, Family.id, Family.name).join(
                EventTarget, EventTarget.event_id == Event.id
            ).join(
                Family, Family.id == EventTarget.family_id
            ).where(
                Family.id.in_(allowed_family_ids),
                Event.title.ilike(search_pattern)
            ).limit(limit)
            
            # Simple deduplication just in case
            seen_events = set()
            for ev, f_id, f_name in self.db.execute(stmt).all():
                if ev.id in seen_events: continue
                seen_events.add(ev.id)
                results.append(SearchResult(
                    id=ev.id,
                    type="event",
                    title=ev.title,
                    subtitle="Event",
                    family_id=f_id,
                    family_name=f_name,
                    route=f"/events/{ev.id}"
                ))
            
            # Find Private events
            stmt_priv = select(Event).join(
                EventTarget, EventTarget.event_id == Event.id
            ).where(
                EventTarget.user_id == user_id,
                EventTarget.audience_type == 'user',
                Event.title.ilike(search_pattern)
            ).limit(limit)
            
            for ev in self.db.execute(stmt_priv).scalars().all():
                if ev.id in seen_events: continue
                seen_events.add(ev.id)
                results.append(SearchResult(
                    id=ev.id,
                    type="event",
                    title=ev.title,
                    subtitle="Private Event",
                    family_id=None,
                    family_name=None,
                    route=f"/events/{ev.id}"
                ))"""

content = content.replace(old_event_search, new_event_search)
with open("backend/app/services/search_service.py", "w") as f:
    f.write(content)
