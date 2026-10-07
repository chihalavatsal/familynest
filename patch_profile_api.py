import re
with open("backend/app/api/v1/profile.py", "r") as f:
    content = f.read()

if "from app.schemas.person import PersonCreate" not in content:
    content = content.replace("from app.schemas.profile import (", "from app.schemas.person import PersonCreate\nfrom app.schemas.profile import (")

onboarding_endpoint = """
@router.post("/profile/onboarding", response_model=PersonListItem)
def complete_profile_onboarding(
    data: PersonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    svc = ProfileService(db)
    person = svc.complete_onboarding(current_user.id, data)
    return PersonListItem.model_validate(person)
"""
if "/profile/onboarding" not in content:
    content = content.replace("@router.get(\"/profile\", response_model=dict)", onboarding_endpoint + "\n@router.get(\"/profile\", response_model=dict)")

with open("backend/app/api/v1/profile.py", "w") as f:
    f.write(content)
