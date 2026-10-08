import psycopg

DB_URL = "postgresql://neondb_owner:npg_NZtKlqwXi18b@ep-flat-river-b4zl2w1t-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require"

with psycopg.connect(DB_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT otp_code, otp_expires_at FROM users WHERE email = 'vatsalchihala26@gmail.com'")
        row = cur.fetchone()
        if row:
            print(f"OTP Code: {row[0]}")
            print(f"Expires at: {row[1]}")
        else:
            print("User not found!")
