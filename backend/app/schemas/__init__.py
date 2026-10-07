"""FamilyNest Pydantic Schemas

Clean separation between database models and API schemas.
Separate request and response schemas to protect private data.
"""

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    LogoutResponse,
)
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.person import (
    PersonCreate,
    PersonUpdate,
    PersonListItem,
    PersonDetailResponse,
    PersonListResponse,
    ProfileStatus,
)
from app.schemas.family import (
    FamilyCreate,
    FamilyUpdate,
    FamilyListItem,
    FamilyResponse,
    FamilyListResponse,
    FamilyMemberCreate,
    FamilyMemberUpdate,
    FamilyMemberResponse,
    FamilyMemberListResponse,
    FamilyRole,
)
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipResponse,
    RelationshipListItem,
    RelationshipListResponse,
    RelationshipType,
    SYMMETRIC_RELATIONSHIPS,
)
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
    InvitationDetailResponse,
    InvitationListResponse,
    PersonClaimResponse,
)
from app.schemas.audit_log import AuditLogBase, AuditLogResponse

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "LogoutResponse",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "PersonCreate",
    "PersonUpdate",
    "PersonListItem",
    "PersonDetailResponse",
    "PersonListResponse",
    "ProfileStatus",
    "FamilyCreate",
    "FamilyUpdate",
    "FamilyListItem",
    "FamilyResponse",
    "FamilyListResponse",
    "FamilyMemberCreate",
    "FamilyMemberUpdate",
    "FamilyMemberResponse",
    "FamilyMemberListResponse",
    "FamilyRole",
    "RelationshipCreate",
    "RelationshipUpdate",
    "RelationshipResponse",
    "RelationshipListItem",
    "RelationshipListResponse",
    "RelationshipType",
    "SYMMETRIC_RELATIONSHIPS",
    "InvitationCreate",
    "InvitationResponse",
    "InvitationDetailResponse",
    "InvitationListResponse",
    "PersonClaimResponse",
    "AuditLogBase",
    "AuditLogResponse",
]
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    AudienceType
)

__all__.extend([
    "NotificationCreate",
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationPreferenceResponse",
    "NotificationPreferenceUpdate",
    "AudienceType"
])
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventAudienceInput, EventParticipantInput, EventParticipantResponse
from app.schemas.activity import ActivityResponse
from app.schemas.profile import *
