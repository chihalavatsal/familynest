import psycopg
DB_URL = "postgresql://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"
with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("UPDATE people SET profile_status = 'claimed' WHERE claimed_by_user_id IS NOT NULL")
    conn.commit()
print("Fixed DB status")
