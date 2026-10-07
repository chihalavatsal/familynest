"""FamilyNest Database Models

Export of all SQLAlchemy 2.x declarative models.
"""

from app.db.models.base import Base
from app.db.models.user import User
from app.db.models.person import Person, ALLOWED_PROFILE_STATUSES
from app.db.models.family import Family, FamilyMember, ALLOWED_FAMILY_ROLES
from app.db.models.relationship import Relationship, ALLOWED_RELATIONSHIP_TYPES
from app.db.models.invitation import Invitation, ALLOWED_INVITATION_STATUSES
from app.db.models.audit_log import AuditLog
from app.db.models.notification import Notification, NotificationTarget, NotificationRecipient, NotificationPreference

__all__ = [
    "Base",
    "User",
    "Person",
    "Family",
    "FamilyMember",
    "Relationship",
    "Invitation",
    "AuditLog",
    "Notification",
    "NotificationTarget",
    "NotificationRecipient",
    "NotificationPreference",
    "ALLOWED_PROFILE_STATUSES",
    "ALLOWED_FAMILY_ROLES",
    "ALLOWED_RELATIONSHIP_TYPES",
    "ALLOWED_INVITATION_STATUSES",
]
from app.db.models.event import Event, EventTarget, EventParticipant
from app.db.models.activity import Activity
from app.db.models.privacy import PersonPrivacySettings, FamilyPrivacySettings

from app.db.models.media import Media, MediaPerson, EventMedia
from app.db.models.album import Album, AlbumMedia, AlbumAllowedUser
from app.db.models.memory import Memory, MemoryPerson, MemoryMedia, MemoryAllowedUser
from app.db.models.employment import Employment
from app.db.models.education import Education
