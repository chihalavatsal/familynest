with open("backend/app/services/profile_service.py", "r") as f:
    content = f.read()

import re
loop_pattern = re.compile(
    r"            for mem in memberships:\n"
    r"                fam = self\.db\.execute\(select\(Family\)\.where\(Family\.id == mem\.family_id\)\)\.scalar_one\(\)\n"
    r"                count = self\.db\.execute\(select\(func\.count\(\)\)\.where\(FamilyMember\.family_id == fam\.id\)\)\.scalar_one\(\)\n"
    r"                families\.append\(FamilySummary\(id=fam\.id, name=fam\.name, role=mem\.role, member_count=count\)\)"
)

optimized_loop = """            if memberships:
                family_ids = [m.family_id for m in memberships]
                fam_records = self.db.execute(select(Family).where(Family.id.in_(family_ids))).scalars().all()
                fam_map = {f.id: f for f in fam_records}
                
                count_rows = self.db.execute(
                    select(FamilyMember.family_id, func.count(FamilyMember.person_id))
                    .where(FamilyMember.family_id.in_(family_ids))
                    .group_by(FamilyMember.family_id)
                ).all()
                count_map = {f_id: cnt for f_id, cnt in count_rows}
                
                for mem in memberships:
                    fam = fam_map.get(mem.family_id)
                    if fam:
                        families.append(FamilySummary(
                            id=fam.id, name=fam.name, role=mem.role, member_count=count_map.get(fam.id, 0)
                        ))"""

content = loop_pattern.sub(optimized_loop, content)
with open("backend/app/services/profile_service.py", "w") as f:
    f.write(content)
