"""Relationship Graph Service — Phase 6.

Read-only graph intelligence layer for calculating dynamic kinship.
Never mutates the database. Never creates relationship records for derived connections.
"""
import uuid
from typing import Optional, List, Dict, Tuple, Set
from collections import deque, defaultdict
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.person import Person
from app.db.models.relationship import Relationship
from app.services.relationship_service import RelationshipService
from app.schemas.relationship_graph import (
    PersonListItem,
    RelationshipPathNode,
    KinshipResult,
    RelatedPersonItem,
    RelatedPersonListResponse,
)

MAX_ALLOWED_DEPTH = 12
DEFAULT_DEPTH = 6
MAX_NODES = 5000


class RelationshipGraphService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.rel_service = RelationshipService(db)
        self._adj: Dict[uuid.UUID, List[Tuple[uuid.UUID, str, Relationship]]] = defaultdict(list)
        self._people_cache: Dict[uuid.UUID, Person] = {}

    def _load_graph(self, user_id: uuid.UUID, include_historical: bool = False) -> None:
        """Loads the authorized graph into memory efficiently."""
        allowed_ids = self.rel_service._get_allowed_person_ids(user_id)
        if not allowed_ids:
            return

        # Fetch people for fast lookup
        people_stmt = select(Person).where(Person.id.in_(allowed_ids))
        for p in self.db.execute(people_stmt).scalars().all():
            self._people_cache[p.id] = p

        # Fetch authorized edges
        edge_stmt = select(Relationship).where(
            Relationship.person_a_id.in_(allowed_ids),
            Relationship.person_b_id.in_(allowed_ids)
        )
        edges = self.db.execute(edge_stmt).scalars().all()

        for rel in edges:
            if not include_historical and not rel.is_current:
                continue
                
            a, b, t = rel.person_a_id, rel.person_b_id, rel.relationship_type
            
            if t == 'parent':
                self._adj[a].append((b, 'child'))
                self._adj[b].append((a, 'parent'))
            elif t == 'child':
                self._adj[a].append((b, 'parent'))
                self._adj[b].append((a, 'child'))
            elif t == 'spouse':
                label = 'spouse' if rel.is_current else 'former_spouse'
                self._adj[a].append((b, label))
                self._adj[b].append((a, label))
            elif t == 'divorced_spouse':
                self._adj[a].append((b, 'former_spouse'))
                self._adj[b].append((a, 'former_spouse'))
            elif t == 'sibling':
                self._adj[a].append((b, 'sibling'))
                self._adj[b].append((a, 'sibling'))
            elif t == 'guardian':
                self._adj[a].append((b, 'ward'))
                self._adj[b].append((a, 'guardian'))

    def _derive_kinship_label(self, path_labels: List[str]) -> Optional[str]:
        """Derives a standard kinship label from an edge path."""
        s = ",".join(path_labels)
        mapping = {
            "parent": "parent",
            "child": "child",
            "spouse": "spouse",
            "former_spouse": "former_spouse",
            "sibling": "sibling",
            "guardian": "guardian",
            "ward": "ward",
            
            "parent,parent": "grandparent",
            "parent,parent,parent": "great_grandparent",
            
            "child,child": "grandchild",
            "child,child,child": "great_grandchild",
            
            "parent,child": "sibling",
            
            "parent,sibling": "uncle_or_aunt",
            "parent,parent,child": "uncle_or_aunt",
            
            "sibling,child": "nephew_or_niece",
            
            "parent,sibling,child": "first_cousin",
            "parent,parent,child,child": "first_cousin",
        }
        return mapping.get(s, "relative")

    def _build_person_summary(self, person_id: uuid.UUID) -> PersonListItem:
        p = self._people_cache[person_id]
        return PersonListItem(id=p.id, first_name=p.first_name, last_name=p.last_name)

    def _bfs_path(self, start_id: uuid.UUID, target_id: uuid.UUID, max_depth: int) -> Optional[List[Tuple[uuid.UUID, str]]]:
        """Finds the shortest path between start and target using BFS."""
        if start_id == target_id:
            return []
            
        queue = deque([(start_id, [])])
        visited = {start_id}
        nodes_visited = 0
        
        while queue:
            curr, path = queue.popleft()
            nodes_visited += 1
            if nodes_visited > MAX_NODES:
                break
                
            if len(path) >= max_depth:
                continue
                
            for nxt, label in self._adj.get(curr, []):
                if nxt not in visited:
                    visited.add(nxt)
                    new_path = path + [(nxt, label)]
                    if nxt == target_id:
                        return new_path
                    queue.append((nxt, new_path))
                    
        return None

    def _get_claimed_person_or_400(self, user_id: uuid.UUID) -> Person:
        stmt = select(Person).where(Person.claimed_by_user_id == user_id)
        person = self.db.execute(stmt).scalar_one_or_none()
        if not person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your account has no claimed Person profile."
            )
        return person

    def _require_access(self, person_id: uuid.UUID, user_id: uuid.UUID) -> None:
        allowed = self.rel_service._get_allowed_person_ids(user_id)
        if person_id not in allowed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found or access denied."
            )

    def get_kinship(
        self, user_id: uuid.UUID, target_id: uuid.UUID, max_depth: int = DEFAULT_DEPTH
    ) -> KinshipResult:
        """How am I related? Returns the shortest path from the claimed person."""
        max_depth = min(max_depth, MAX_ALLOWED_DEPTH)
        source = self._get_claimed_person_or_400(user_id)
        self._require_access(target_id, user_id)
        
        if source.id == target_id:
            return KinshipResult(
                source_person=PersonListItem(id=source.id, first_name=source.first_name, last_name=source.last_name),
                target_person=PersonListItem(id=source.id, first_name=source.first_name, last_name=source.last_name),
                relationship="self",
                distance=0,
                path=[]
            )
            
        # Try current relationships first
        self._load_graph(user_id, include_historical=False)
        path = self._bfs_path(source.id, target_id, max_depth)
        
        # Fallback to historical if no current path
        if path is None:
            self._load_graph(user_id, include_historical=True)
            path = self._bfs_path(source.id, target_id, max_depth)
            
        if path is None:
            # No connection
            target_p = self.db.execute(select(Person).where(Person.id == target_id)).scalar_one()
            return KinshipResult(
                source_person=PersonListItem(id=source.id, first_name=source.first_name, last_name=source.last_name),
                target_person=PersonListItem(id=target_p.id, first_name=target_p.first_name, last_name=target_p.last_name),
                relationship=None,
                distance=0,
                path=[]
            )
            
        # Build path response
        node_path = []
        labels = []
        for p_id, label in path:
            node_path.append(RelationshipPathNode(
                person=self._build_person_summary(p_id),
                relationship=label
            ))
            labels.append(label)
            
        kinship = self._derive_kinship_label(labels)
        
        return KinshipResult(
            source_person=PersonListItem(id=source.id, first_name=source.first_name, last_name=source.last_name),
            target_person=self._build_person_summary(target_id),
            relationship=kinship,
            distance=len(path),
            path=node_path
        )

    def _traverse_tree(self, start_id: uuid.UUID, allowed_edges: Set[str], max_depth: int) -> List[RelatedPersonItem]:
        """Generic BFS traversal restricting edges to allowed directions (e.g. only 'parent')."""
        results = []
        queue = deque([(start_id, [])])
        visited = {start_id}
        nodes_visited = 0
        
        while queue:
            curr, path = queue.popleft()
            nodes_visited += 1
            if nodes_visited > MAX_NODES:
                break
                
            if len(path) >= max_depth:
                continue
                
            for nxt, label in self._adj.get(curr, []):
                if label in allowed_edges and nxt not in visited:
                    visited.add(nxt)
                    new_path = path + [(nxt, label)]
                    
                    labels = [lbl for _, lbl in new_path]
                    kinship = self._derive_kinship_label(labels)
                    
                    path_nodes = [
                        RelationshipPathNode(person=self._build_person_summary(p), relationship=l)
                        for p, l in new_path
                    ]
                    
                    results.append(RelatedPersonItem(
                        person=self._build_person_summary(nxt),
                        relationship=kinship,
                        distance=len(new_path),
                        path=path_nodes
                    ))
                    queue.append((nxt, new_path))
                    
        return results

    def get_ancestors(self, user_id: uuid.UUID, person_id: uuid.UUID, max_depth: int = DEFAULT_DEPTH) -> RelatedPersonListResponse:
        max_depth = min(max_depth, MAX_ALLOWED_DEPTH)
        self._require_access(person_id, user_id)
        self._load_graph(user_id, include_historical=False)
        items = self._traverse_tree(person_id, {"parent"}, max_depth)
        return RelatedPersonListResponse(items=items, total=len(items))

    def get_descendants(self, user_id: uuid.UUID, person_id: uuid.UUID, max_depth: int = DEFAULT_DEPTH) -> RelatedPersonListResponse:
        max_depth = min(max_depth, MAX_ALLOWED_DEPTH)
        self._require_access(person_id, user_id)
        self._load_graph(user_id, include_historical=False)
        items = self._traverse_tree(person_id, {"child"}, max_depth)
        return RelatedPersonListResponse(items=items, total=len(items))

    def get_siblings(self, user_id: uuid.UUID, person_id: uuid.UUID) -> RelatedPersonListResponse:
        self._require_access(person_id, user_id)
        self._load_graph(user_id, include_historical=False)
        
        siblings = set()
        items = []
        
        # Explicit siblings + shared parents
        for nxt, label in self._adj.get(person_id, []):
            if label == "sibling":
                if nxt not in siblings:
                    siblings.add(nxt)
                    items.append(RelatedPersonItem(
                        person=self._build_person_summary(nxt),
                        relationship="sibling",
                        distance=1,
                        path=[RelationshipPathNode(person=self._build_person_summary(nxt), relationship="sibling")]
                    ))
            elif label == "parent":
                # Find children of this parent (our siblings)
                for step_sibling, slabel in self._adj.get(nxt, []):
                    if slabel == "child" and step_sibling != person_id and step_sibling not in siblings:
                        siblings.add(step_sibling)
                        items.append(RelatedPersonItem(
                            person=self._build_person_summary(step_sibling),
                            relationship="sibling",
                            distance=2,
                            path=[
                                RelationshipPathNode(person=self._build_person_summary(nxt), relationship="parent"),
                                RelationshipPathNode(person=self._build_person_summary(step_sibling), relationship="child")
                            ]
                        ))
                        
        return RelatedPersonListResponse(items=items, total=len(items))

    def get_direct_relationships(self, user_id: uuid.UUID, person_id: uuid.UUID, include_historical: bool = False) -> RelatedPersonListResponse:
        self._require_access(person_id, user_id)
        self._load_graph(user_id, include_historical=include_historical)
        
        items = []
        for nxt, label in self._adj.get(person_id, []):
            items.append(RelatedPersonItem(
                person=self._build_person_summary(nxt),
                relationship=self._derive_kinship_label([label]),
                distance=1,
                path=[RelationshipPathNode(person=self._build_person_summary(nxt), relationship=label)]
            ))
            
        return RelatedPersonListResponse(items=items, total=len(items))
