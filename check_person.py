import psycopg
DB_URL = "postgresql://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT person_id FROM invitations WHERE id = '19eb8c69-aad4-4b21-82e6-3af361601d9c'")
        row = cur.fetchone()
        if row:
            person_id = row[0]
            print(f"Person ID: {person_id}")
            cur.execute(f"SELECT id, first_name, last_name, claimed_by_user_id FROM people WHERE id = '{person_id}'")
            person_row = cur.fetchone()
            if person_row:
                print(f"Person exists: {person_row}")
            else:
                print("Person DOES NOT EXIST!")
        else:
            print("Invitation not found.")
