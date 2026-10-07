from app.db.database import SessionLocal
from app.db.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'my_fake_test_99@test.com').first()
if user:
    print(f"User exists: {user.email}, otp_code: {user.otp_code}, expires: {user.otp_expires_at}")
else:
    print("User DOES NOT EXIST in database!")
