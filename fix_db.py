import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        # Get the family they created
        cur.execute("SELECT id, created_by_user_id FROM families;")
        families = cur.fetchall()
        for f in families:
            family_id, user_id = f
            # Get the claimed person for this user
            cur.execute("SELECT id FROM people WHERE claimed_by_user_id = %s;", (user_id,))
            person = cur.fetchone()
            if person:
                person_id = person[0]
                # Check if they are in family_members
                cur.execute("SELECT 1 FROM family_members WHERE family_id = %s AND person_id = %s;", (family_id, person_id))
                if not cur.fetchone():
                    # Insert them as owner!
                    print(f"Fixing ghost creator bug for Family {family_id}, Person {person_id}")
                    cur.execute("""
                        INSERT INTO family_members (family_id, person_id, role, joined_at, created_at)
                        VALUES (%s, %s, 'owner', NOW(), NOW())
                    """, (family_id, person_id))
        conn.commit()
print("Done")
