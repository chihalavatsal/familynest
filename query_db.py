import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URL).replace("postgresql+asyncpg", "postgresql"))

with engine.connect() as conn:
    families = conn.execute(text("SELECT id, name, created_by_user_id FROM families;")).fetchall()
    members = conn.execute(text("SELECT family_id, person_id, role FROM family_members;")).fetchall()
    people = conn.execute(text("SELECT id, claimed_by_user_id, first_name FROM people;")).fetchall()

    print("Families:", families)
    print("Members:", members)
    print("People:", people)
