import sys
import uuid
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.person_claim_service import PersonClaimService
from app.db.models.user import User

engine = create_engine("postgresql+psycopg://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

user = db.query(User).filter(User.email == 'vatsalchihala26@gmail.com').first()
user_id = user.id

invitation_id = uuid.UUID("19eb8c69-aad4-4b21-82e6-3af361601d9c")

service = PersonClaimService(db)
try:
    res = service.accept_invitation_by_id(user_id=user_id, invitation_id=invitation_id)
    print("SUCCESS:", res)
except Exception as e:
    print("FAILED:", type(e))
    import traceback
    traceback.print_exc()

