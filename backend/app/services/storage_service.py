import uuid
from typing import Dict, Any, Optional

class StorageService:
    """
    Abstract StorageService for Phase 16.
    Cloudinary integration will be added here in a later phase.
    """
    
    def __init__(self):
        self.provider = "unavailable"
        
    def is_available(self) -> bool:
        """Returns False since actual storage is not configured yet."""
        return False
        
    def create_upload_request(self, original_filename: str, mime_type: str, user_id: uuid.UUID, family_id: uuid.UUID) -> Dict[str, Any]:
        """
        Creates a secure upload signature/authorization for the frontend.
        """
        if not self.is_available():
            raise NotImplementedError("Storage is not configured yet. Cloudinary integration pending.")
            
        return {
            "upload_url": "unavailable",
            "signature": "unavailable",
            "provider": self.provider
        }
        
    def get_access_url(self, storage_object_key: str) -> Optional[str]:
        """
        Returns a temporary signed URL or canonical URL for the media.
        """
        if not self.is_available() or not storage_object_key:
            return None
        # Once connected, this will generate a Cloudinary URL
        return None
        
    def delete_object(self, storage_object_key: str) -> bool:
        """
        Deletes the binary object from storage.
        """
        if not self.is_available() or not storage_object_key:
            return True
        return False
        
    def object_exists(self, storage_object_key: str) -> bool:
        """
        Verifies if an object actually exists in storage.
        """
        return False
