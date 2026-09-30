import re
from typing import Generator
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.models.base import Base


def normalize_database_url(url: str) -> str:
    """Normalize database URL for SQLAlchemy 2.x and Neon PostgreSQL.
    
    1. Strips any leading/trailing quotes or whitespace.
    2. Converts driver schemes (postgres:// or postgresql:// -> postgresql+psycopg://)
    3. Ensures sslmode=require is present for Neon connections.
    """
    if not url:
        return url

    # Strip surrounding quotes and whitespace
    url = url.strip("'\" \t\r\n")

    # Replace legacy or unadorned scheme with psycopg 3
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]

    # Parse and enforce sslmode=require
    parsed = urlparse(url)
    if "postgresql" in parsed.scheme:
        query_dict = dict(parse_qsl(parsed.query))
        if "sslmode" not in query_dict:
            query_dict["sslmode"] = "require"
            new_query = urlencode(query_dict)
            parsed = parsed._replace(query=new_query)
            url = urlunparse(parsed)

    return url


def get_redacted_database_url(url: str) -> str:
    """Return database URL with password masked for safe logging/inspection."""
    if not url:
        return "None"
    # Strip any enclosing quotes
    url = url.strip("'\" \t\r\n")
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username or ''}:****@{parsed.hostname or ''}"
            if parsed.port:
                netloc += f":{parsed.port}"
            redacted = parsed._replace(netloc=netloc)
            return urlunparse(redacted)
        return url
    except Exception:
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", url)


# Resolved and normalized DATABASE_URL
DATABASE_URL = normalize_database_url(settings.DATABASE_URL or "")

# SQLAlchemy 2.x Engine (created when DATABASE_URL is configured)
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=settings.DEBUG and settings.ENVIRONMENT == "development",
    )
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
else:
    engine = None
    SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    """Dependency for delivering clean, request-scoped database sessions.
    
    Guarantees session rollback on exception and deterministic closing.
    """
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured. Please set DATABASE_URL in your .env file "
            "or environment variables (e.g. postgresql+psycopg://user:password@host/database?sslmode=require)."
        )
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
