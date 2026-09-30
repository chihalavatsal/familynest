"""FamilyNest Seed Script Structure

Foundation for future seed commands/scripts.
NOTE: Does NOT insert data automatically into Neon database to avoid polluting
the development database.
"""
import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)


def seed_database(db: Session) -> None:
    """Entry point for future seed execution.
    
    Will populate foundational development records when explicitly invoked.
    """
    logger.info("Seed runner initialized. No automatic test data inserted.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
