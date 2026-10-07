import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, text

from app.db.models.family import Family, FamilyMember
from app.db.models.person import Person
from app.db.models.memory import Memory, MemoryAllowedUser
from app.db.models.album import Album, AlbumAllowedUser
from app.db.models.event import Event, EventTarget
from app.schemas.search import SearchResult, SearchResponse

class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def _get_user_families(self, user_id: uuid.UUID):
        stmt = select(Family.id, Family.name).join(FamilyMember, FamilyMember.family_id == Family.id).join(Person, Person.id == FamilyMember.person_id).where(Person.claimed_by_user_id == user_id)
        return {f.id: f.name for f in self.db.execute(stmt).all()}

    def search(self, user_id: uuid.UUID, q: str, type_filter: Optional[str] = None, family_id: Optional[uuid.UUID] = None, limit: int = 10) -> SearchResponse:
        q = q.strip()
        if not q or len(q) < 2:
            return SearchResponse(items=[], total=0)
            
        search_pattern = f"%{q}%"
        families_map = self._get_user_families(user_id)
        allowed_family_ids = list(families_map.keys())
        
        if family_id:
            if family_id not in families_map:
                return SearchResponse(items=[], total=0)
            allowed_family_ids = [family_id]

        results = []
        
        # 1. Families
        if not type_filter or type_filter == 'family':
            stmt = select(Family).where(
                Family.id.in_(allowed_family_ids),
                Family.name.ilike(search_pattern)
            ).limit(limit)
            
            for fam in self.db.execute(stmt).scalars().all():
                results.append(SearchResult(
                    id=fam.id,
                    type="family",
                    title=fam.name,
                    subtitle="Family",
                    family_id=fam.id,
                    family_name=fam.name,
                    route=f"/families/{fam.id}"
                ))

        # 2. People
        if not type_filter or type_filter == 'person':
            # A person can be in multiple families. We return them annotated with the family we found them in.
            stmt = select(Person, Family.id, Family.name).join(
                FamilyMember, FamilyMember.person_id == Person.id
            ).join(
                Family, Family.id == FamilyMember.family_id
            ).where(
                Family.id.in_(allowed_family_ids),
                or_(
                    Person.first_name.ilike(search_pattern),
                    Person.last_name.ilike(search_pattern)
                )
            ).limit(limit)
            
            for person, f_id, f_name in self.db.execute(stmt).all():
                name = person.first_name
                if person.last_name: name += f" {person.last_name}"
                results.append(SearchResult(
                    id=person.id,
                    type="person",
                    title=name,
                    subtitle=person.nickname or "Person",
                    family_id=f_id,
                    family_name=f_name,
                    route=f"/people/{person.id}"
                ))

        # 3. Memories
        if not type_filter or type_filter == 'memory':
            stmt = select(Memory).where(
                Memory.family_id.in_(allowed_family_ids),
                Memory.title.ilike(search_pattern),
                or_(
                    Memory.visibility == 'family',
                    Memory.id.in_(select(MemoryAllowedUser.memory_id).where(MemoryAllowedUser.user_id == user_id))
                )
            ).limit(limit)
            
            for mem in self.db.execute(stmt).scalars().all():
                results.append(SearchResult(
                    id=mem.id,
                    type="memory",
                    title=mem.title,
                    subtitle="Memory",
                    family_id=mem.family_id,
                    family_name=families_map[mem.family_id],
                    route=f"/memories/{mem.id}"
                ))

        # 4. Albums
        if not type_filter or type_filter == 'album':
            stmt = select(Album).where(
                Album.family_id.in_(allowed_family_ids),
                Album.title.ilike(search_pattern),
                or_(
                    Album.visibility == 'family',
                    Album.id.in_(select(AlbumAllowedUser.album_id).where(AlbumAllowedUser.user_id == user_id))
                )
            ).limit(limit)
            
            for alb in self.db.execute(stmt).scalars().all():
                results.append(SearchResult(
                    id=alb.id,
                    type="album",
                    title=alb.title,
                    subtitle="Album",
                    family_id=alb.family_id,
                    family_name=families_map[alb.family_id],
                    route=f"/albums/{alb.id}"
                ))

        # 5. Events
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
                ))

        # Simple deterministic ranking (Exact > Starts > Word > Contains) can be approximated in python since results are limited.
        def rank_score(item: SearchResult) -> int:
            title = item.title.lower()
            lq = q.lower()
            if title == lq: return 0
            if title.startswith(lq): return 1
            if f" {lq}" in title: return 2
            return 3
            
        results.sort(key=rank_score)
        
        # Enforce global limit if there's no type filter
        if not type_filter:
            results = results[:limit]

        return SearchResponse(items=results, total=len(results))
