import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM families;")
        print("Families:", cur.fetchall())
        cur.execute("SELECT person_id, family_id, role FROM family_members;")
        print("Members:", cur.fetchall())
