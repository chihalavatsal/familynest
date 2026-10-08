import sys
import uuid
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.graph_service import FamilyGraphService
from app.db.models.user import User
from app.db.models.family import Family

engine = create_engine("postgresql+psycopg://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

user = db.query(User).filter(User.email == 'vatsalchihala26@gmail.com').first()
user_id = user.id
family_id = uuid.UUID("4d097ccc-0dd3-4b49-9003-6bfcdabdbc4c")

service = FamilyGraphService(db)
try:
    res = service.get_family_tree(family_id=family_id, current_user_id=user_id)
    print("SUCCESS")
except Exception as e:
    print("FAILED:", type(e))
    import traceback
    traceback.print_exc()

