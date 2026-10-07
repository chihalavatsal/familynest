import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, created_by_user_id FROM families;")
        print("Families:", cur.fetchall())
        
        cur.execute("SELECT family_id, person_id, role FROM family_members;")
        print("Members:", cur.fetchall())
        
        cur.execute("SELECT id, claimed_by_user_id, first_name FROM people;")
        print("People:", cur.fetchall())
