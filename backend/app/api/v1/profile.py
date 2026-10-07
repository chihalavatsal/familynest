from fastapi import APIRouter, Depends
import uuid

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.schemas.person import PersonCreate
from app.schemas.profile import (
    CurrentUserProfile, PersonProfileUpdate, PrivacySettingsResponse, PrivacySettingsUpdate,
    ProfileCompletenessResponse, DashboardResponse, FamilyOverviewResponse, PersonListItem
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="", tags=["profile"])


@router.post("/profile/onboarding", response_model=PersonListItem)
def complete_profile_onboarding(
    data: PersonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    person = svc.complete_onboarding(current_user.id, data)
    return PersonListItem.model_validate(person)

@router.get("/profile", response_model=dict)
def get_current_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    person = svc.get_current_user_person(current_user.id)
    return {
        "user": CurrentUserProfile.model_validate(current_user),
        "person": PersonListItem.model_validate(person) if person else None
    }

@router.patch("/profile/person", response_model=PersonListItem)
def update_current_person(
    data: PersonProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    person = svc.update_person_profile(current_user.id, data)
    return PersonListItem.model_validate(person)

@router.get("/profile/privacy", response_model=PrivacySettingsResponse)
def get_privacy_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    return svc.get_privacy_settings(current_user.id)

@router.patch("/profile/privacy", response_model=PrivacySettingsResponse)
def update_privacy_settings(
    data: PrivacySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    return svc.update_privacy_settings(current_user.id, data)

@router.get("/profile/completeness", response_model=ProfileCompletenessResponse)
def get_profile_completeness(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    return svc.get_profile_completeness(current_user.id)

@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    return svc.get_dashboard(current_user.id)

@router.get("/families/{family_id}/overview", response_model=FamilyOverviewResponse)
def get_family_overview(
    family_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    return svc.get_family_overview(family_id, current_user.id)
