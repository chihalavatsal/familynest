from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# SQLAlchemy 2.x Engine
engine = create_engine(
    settings.DATABASE_URL or "postgresql+psycopg://familynest_user:familynest_dev_password@localhost:5432/familynest",
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing database session to API endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
