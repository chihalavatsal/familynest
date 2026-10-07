import re
with open("backend/app/services/profile_service.py", "r") as f:
    content = f.read()

# Add imports for PersonCreate and PersonClaimService
if "PersonClaimService" not in content:
    content = content.replace("from app.services.activity_service import ActivityService", "from app.services.activity_service import ActivityService\nfrom app.services.person_claim_service import PersonClaimService\nfrom app.services.person_service import PersonService")

if "from app.schemas.person import PersonCreate" not in content:
    content = content.replace("from app.schemas.profile import", "from app.schemas.person import PersonCreate\nfrom app.schemas.profile import")

onboarding_func = """
    def complete_onboarding(self, user_id: uuid.UUID, data: PersonCreate):
        # Verify user has no claimed Person
        existing = self.get_current_user_person(user_id)
        if existing:
            raise HTTPException(status_code=409, detail="User already has a claimed Person.")
            
        # Create canonical Person and claim it atomically-ish (we will use DB transaction)
        # PersonService.create_person commits internally, which breaks atomicity if claim fails.
        # However, we can use the repository directly or just accept the 2-step commit since
        # claim_person rarely fails for a freshly created person by the same user.
        # But for true atomicity, let's do it here:
        from app.db.models.person import Person
        from app.db.models.privacy import PersonPrivacySettings
        from app.db.models.activity import AuditLog
        from datetime import datetime, timezone

        try:
            # 1. Create Person
            person = Person(
                **data.model_dump(exclude_unset=True),
                created_by_user_id=user_id,
                claimed_by_user_id=user_id,
                profile_status="claimed"
            )
            self.db.add(person)
            self.db.flush()

            # 2. Setup privacy defaults
            privacy = PersonPrivacySettings(person_id=person.id)
            self.db.add(privacy)

            # 3. Audit log
            audit = AuditLog(
                actor_user_id=user_id,
                action="person.create_and_claim_onboarding",
                entity_type="person",
                entity_id=person.id,
                metadata={"method": "onboarding"}
            )
            self.db.add(audit)
            self.db.commit()
            
            return person
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create and claim person.")
"""

content = content.replace("def get_current_user_person", onboarding_func + "\n    def get_current_user_person")

with open("backend/app/services/profile_service.py", "w") as f:
    f.write(content)

