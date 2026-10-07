with open("backend/app/services/memory_service.py", "r") as f:
    content = f.read()

import_str = "from app.db.models.memory import MemoryAllowedUser"
if import_str not in content:
    content = content.replace("from app.db.models.memory import", "from app.db.models.memory import MemoryAllowedUser,")

create_logic = """
        self.db.commit()
        
        # Handle allowed users
        if getattr(memory_data, 'visibility', 'family') == 'selected_members' and getattr(memory_data, 'allowed_user_ids', None):
            for uid in memory_data.allowed_user_ids:
                if self.authz.can_view_family(uid, memory_data.family_id):
                    self.db.add(MemoryAllowedUser(memory_id=memory.id, user_id=uid))
            self.db.commit()
            
        return memory"""

content = content.replace("        self.db.commit()\n        return memory", create_logic, 1)

with open("backend/app/services/memory_service.py", "w") as f:
    f.write(content)

with open("backend/app/services/album_service.py", "r") as f:
    content = f.read()

import_str = "from app.db.models.album import AlbumAllowedUser"
if import_str not in content:
    content = content.replace("from app.db.models.album import", "from app.db.models.album import AlbumAllowedUser,")

create_logic2 = """
        self.db.commit()
        
        # Handle allowed users
        if getattr(album_data, 'visibility', 'family') == 'selected_members' and getattr(album_data, 'allowed_user_ids', None):
            for uid in album_data.allowed_user_ids:
                if self.authz.can_view_family(uid, album_data.family_id):
                    self.db.add(AlbumAllowedUser(album_id=album.id, user_id=uid))
            self.db.commit()
            
        return album"""

content = content.replace("        self.db.commit()\n        return album", create_logic2, 1)

with open("backend/app/services/album_service.py", "w") as f:
    f.write(content)

