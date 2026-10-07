import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, first_name FROM people;")
        people = cur.fetchall()
        print("People:", people)
        
        cur.execute("SELECT person_a_id, person_b_id, relationship_type FROM relationships;")
        print("Relationships:", cur.fetchall())
