import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        # Find the user
        cur.execute("SELECT id, email FROM users WHERE email LIKE '%%gmail%%';")
        user = cur.fetchone()
        if not user:
            print("User not found!")
            exit(1)
            
        user_id = user[0]
        print(f"Found user: {user[1]} ({user_id})")
        
        # We want to delete all PEOPLE except the one claimed by this user
        # But wait, what about families? What about family_members? What about relationships?
        # Let's just delete all people who are NOT claimed by this user.
        # Cascading deletes might handle the rest, but let's be safe.
        
        # 1. Get the claimed person ID
        cur.execute("SELECT id FROM people WHERE claimed_by_user_id = %s;", (user_id,))
        claimed = cur.fetchone()
        claimed_id = claimed[0] if claimed else None
        
        print(f"Claimed person ID: {claimed_id}")
        
        # 2. Delete all relationships
        cur.execute("DELETE FROM relationships;")
        print("Deleted all relationships")
        
        # 3. Delete all family_members except for the claimed person
        if claimed_id:
            cur.execute("DELETE FROM family_members WHERE person_id != %s;", (claimed_id,))
        else:
            cur.execute("DELETE FROM family_members;")
        print("Deleted family_members")
        
        # 4. Delete all people except the claimed person
        if claimed_id:
            cur.execute("DELETE FROM people WHERE id != %s;", (claimed_id,))
        else:
            cur.execute("DELETE FROM people;")
        print("Deleted people")
        
        conn.commit()
        print("Done!")
