import re

with open('backend/app/services/profile_service.py', 'r') as f:
    content = f.read()

old_code = """
        # Relationship Summary
        rel_summary = RelationshipSummary(parents_count=0, children_count=0, siblings_count=0, spouses_count=0)
        if person:
            from sqlalchemy import or_
            parents = self.db.execute(select(func.count()).where(Relationship.person_b_id == person.id, Relationship.relationship_type == "parent")).scalar_one()
            children = self.db.execute(select(func.count()).where(Relationship.person_a_id == person.id, Relationship.relationship_type == "parent")).scalar_one()
            siblings = self.db.execute(select(func.count()).where(or_(Relationship.person_a_id == person.id, Relationship.person_b_id == person.id), Relationship.relationship_type == "sibling")).scalar_one()
            spouses = self.db.execute(select(func.count()).where(or_(Relationship.person_a_id == person.id, Relationship.person_b_id == person.id), Relationship.relationship_type == "spouse")).scalar_one()
            rel_summary = RelationshipSummary(parents_count=parents, children_count=children, siblings_count=siblings, spouses_count=spouses)
"""

new_code = """
        # Relationship Summary
        rel_summary = RelationshipSummary(parents_count=0, children_count=0, siblings_count=0, spouses_count=0)
        if person:
            from sqlalchemy import or_
            # Optimize 4 sequential queries into 1 to reduce Neon DB latency
            rows = self.db.execute(
                select(Relationship.relationship_type, Relationship.person_a_id, Relationship.person_b_id)
                .where(or_(Relationship.person_a_id == person.id, Relationship.person_b_id == person.id))
            ).all()
            
            p_cnt = sum(1 for r in rows if r.relationship_type == 'parent' and r.person_b_id == person.id)
            c_cnt = sum(1 for r in rows if r.relationship_type == 'parent' and r.person_a_id == person.id)
            s_cnt = sum(1 for r in rows if r.relationship_type == 'sibling')
            sp_cnt = sum(1 for r in rows if r.relationship_type == 'spouse')
            
            rel_summary = RelationshipSummary(parents_count=p_cnt, children_count=c_cnt, siblings_count=s_cnt, spouses_count=sp_cnt)
"""

content = content.replace(old_code, new_code)

with open('backend/app/services/profile_service.py', 'w') as f:
    f.write(content)
