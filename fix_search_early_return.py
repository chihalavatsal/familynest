with open("backend/app/services/search_service.py", "r") as f:
    content = f.read()

old_code = """        families_map = self._get_user_families(user_id)
        allowed_family_ids = list(families_map.keys())
        
        if not allowed_family_ids:
            return SearchResponse(items=[], total=0)
            
        if family_id:"""

new_code = """        families_map = self._get_user_families(user_id)
        allowed_family_ids = list(families_map.keys())
        
        if family_id:"""

content = content.replace(old_code, new_code)
with open("backend/app/services/search_service.py", "w") as f:
    f.write(content)
