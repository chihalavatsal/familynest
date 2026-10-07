import asyncio
import asyncpg
import os

async def main():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    
    families = await conn.fetch("SELECT id, name, created_by_user_id FROM families;")
    print("Families:", families)
    
    members = await conn.fetch("SELECT family_id, person_id, role FROM family_members;")
    print("Members:", members)
    
    people = await conn.fetch("SELECT id, claimed_by_user_id, first_name FROM people;")
    print("People:", people)
    
    await conn.close()

asyncio.run(main())
