import psycopg
DB_URL = "postgresql://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, status, invited_email, expires_at FROM invitations WHERE invited_email = 'vatsalchihala26@gmail.com'")
        rows = cur.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Status: {row[1]}, Email: {row[2]}, Expires: {row[3]}")
