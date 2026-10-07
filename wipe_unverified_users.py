from app.db.database import SessionLocal
from app.db.models.user import User

db = SessionLocal()
try:
    users = db.query(User).filter(User.is_verified == False).all()
    for u in users:
        print(f"Deleting user: {u.email}")
        db.delete(u)
    db.commit()
    print("Unverified users deleted.")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
