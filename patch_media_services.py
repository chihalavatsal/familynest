import re

def patch_memory_service():
    with open("backend/app/services/memory_service.py", "r") as f:
        content = f.read()
    
    # Imports
    content = content.replace("from app.repositories.memory_repository import MemoryRepository", "from app.repositories.memory_repository import MemoryRepository\nfrom app.services.authz_service import AuthzService\nfrom app.db.models.memory import MemoryAllowedUser")
    
    # Init
    content = content.replace("self.repo = MemoryRepository(db)", "self.repo = MemoryRepository(db)\n        self.authz = AuthzService(db)")
    
    # require_access
    content = content.replace(
        "    def _require_access(self, user_id: uuid.UUID, family_id: uuid.UUID):\n        if not self.repo.user_has_family_access(user_id, family_id):\n            raise HTTPException(status_code=403, detail=\"Not authorized to access memories for this family.\")",
        ""
    )
    
    content = content.replace("self._require_access(user_id, memory_data.family_id)", "self.authz.require_family_view(user_id, memory_data.family_id)")
    
    # get_by_id
    content = content.replace(
        "self._require_access(user_id, mem.family_id)", 
        "self.authz.require_memory_view(user_id, mem)"
    )
    
    # list_for_family
    content = content.replace(
        "self._require_access(user_id, family_id)", 
        "self.authz.require_family_view(user_id, family_id)"
    )
    
    # update create to handle visibility
    content = content.replace(
        "created_by_user_id=user_id",
        "created_by_user_id=user_id,\n            visibility=getattr(memory_data, 'visibility', 'family')"
    )
    
    with open("backend/app/services/memory_service.py", "w") as f:
        f.write(content)

def patch_album_service():
    with open("backend/app/services/album_service.py", "r") as f:
        content = f.read()
    
    content = content.replace("from app.repositories.memory_repository import MemoryRepository", "from app.repositories.memory_repository import MemoryRepository\nfrom app.services.authz_service import AuthzService")
    content = content.replace("self.mem_repo = MemoryRepository(db) # For auth check", "self.authz = AuthzService(db)")
    content = content.replace(
        "    def _require_access(self, user_id: uuid.UUID, family_id: uuid.UUID):\n        if not self.mem_repo.user_has_family_access(user_id, family_id):\n            raise HTTPException(status_code=403, detail=\"Not authorized to access albums for this family.\")",
        ""
    )
    content = content.replace("self._require_access(user_id, album_data.family_id)", "self.authz.require_family_view(user_id, album_data.family_id)")
    content = content.replace("self._require_access(user_id, album.family_id)", "self.authz.require_album_view(user_id, album)")
    content = content.replace("self._require_access(user_id, family_id)", "self.authz.require_family_view(user_id, family_id)")
    
    content = content.replace(
        "created_by_user_id=user_id",
        "created_by_user_id=user_id,\n            visibility=getattr(album_data, 'visibility', 'family')"
    )
    
    with open("backend/app/services/album_service.py", "w") as f:
        f.write(content)

def patch_media_service():
    with open("backend/app/services/media_service.py", "r") as f:
        content = f.read()
        
    content = content.replace("from app.repositories.memory_repository import MemoryRepository", "from app.services.authz_service import AuthzService")
    content = content.replace("self.mem_repo = MemoryRepository(db) # For auth check", "self.authz = AuthzService(db)")
    content = content.replace(
        "    def _require_access(self, user_id: uuid.UUID, family_id: uuid.UUID):\n        if not self.mem_repo.user_has_family_access(user_id, family_id):\n            raise HTTPException(status_code=403, detail=\"Not authorized to access media for this family.\")",
        ""
    )
    content = content.replace("self._require_access(user_id, media_data.family_id)", "self.authz.require_family_view(user_id, media_data.family_id)")
    content = content.replace("self._require_access(user_id, media.family_id)", "self.authz.require_family_view(user_id, media.family_id)")
    content = content.replace("self._require_access(user_id, family_id)", "self.authz.require_family_view(user_id, family_id)")
    
    with open("backend/app/services/media_service.py", "w") as f:
        f.write(content)

patch_memory_service()
patch_album_service()
patch_media_service()
