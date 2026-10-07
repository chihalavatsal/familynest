import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        # Find the user
        cur.execute("SELECT id, email FROM users WHERE email LIKE '%%gmail%%';")
        user = cur.fetchone()
        user_id = user[0]
        
        cur.execute("SELECT id FROM people WHERE claimed_by_user_id = %s;", (user_id,))
        claimed = cur.fetchone()
        claimed_id = claimed[0] if claimed else None
        
        cur.execute("DELETE FROM invitations;")
        print("Deleted invitations")
        
        cur.execute("DELETE FROM relationships;")
        print("Deleted relationships")
        
        if claimed_id:
            cur.execute("DELETE FROM family_members WHERE person_id != %s;", (claimed_id,))
            cur.execute("DELETE FROM people WHERE id != %s;", (claimed_id,))
        else:
            cur.execute("DELETE FROM family_members;")
            cur.execute("DELETE FROM people;")
            
        print("Deleted people")
        
        conn.commit()
        print("Done!")
