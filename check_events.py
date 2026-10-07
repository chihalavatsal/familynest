import psycopg
import os

url = os.environ['DATABASE_URL'].replace("postgresql+psycopg://", "postgresql://")
with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, start_date, end_date, start_datetime, end_datetime, all_day FROM events;")
        print("Events:", cur.fetchall())
