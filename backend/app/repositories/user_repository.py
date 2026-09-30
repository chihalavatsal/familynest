import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models.user import User


class UserRepository:
    """Repository handling database access for User entities."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Retrieve user by primary key UUID."""
        statement = select(User).where(User.id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by normalized email address."""
        statement = select(User).where(User.email == email.lower().strip())
        return self.db.execute(statement).scalar_one_or_none()

    def create(
        self,
        email: str,
        password_hash: str,
        display_name: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
    ) -> User:
        """Create and persist a new User record."""
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            display_name=display_name.strip() if display_name else None,
            is_active=is_active,
            is_verified=is_verified,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        """Commit updates to an existing User record."""
        self.db.commit()
        self.db.refresh(user)
        return user
