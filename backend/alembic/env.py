import sys
from logging.config import fileConfig
from pathlib import Path
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure backend root is in python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.config import settings
from app.db.database import normalize_database_url
from app.db.models.base import Base
# Import models so Alembic metadata includes all entities
import app.db.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database URL dynamically from environment / settings
raw_url = settings.DATABASE_URL or ""
normalized_url = normalize_database_url(raw_url)

if not normalized_url:
    # Set dummy URL so offline inspections don't fail immediately,
    # but online execution will validate presence of real DATABASE_URL.
    config.set_main_option("sqlalchemy.url", "postgresql+psycopg://placeholder:placeholder@localhost/placeholder")
else:
    config.set_main_option("sqlalchemy.url", normalized_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with SSL support."""
    if not normalized_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Please configure DATABASE_URL in your .env file "
            "with your Neon PostgreSQL connection string (e.g. postgresql+psycopg://user:password@host/database?sslmode=require)."
        )

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = normalized_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
