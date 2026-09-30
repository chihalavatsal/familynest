from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, get_redacted_database_url
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.people import router as people_router

api_router = APIRouter()

# Mount Authentication router (/api/v1/auth)
api_router.include_router(auth_router)

# Mount People router (/api/v1/people)
api_router.include_router(people_router)


@api_router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational status."""
    return {
        "status": "healthy",
        "app": "FamilyNest API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@api_router.get("/health/db", tags=["Health"])
def database_health_check(db: Session = Depends(get_db)):
    """Backend database connectivity check for Neon PostgreSQL.
    
    Verifies that the backend can connect to the configured Neon database.
    Redacts all credentials and secrets.
    """
    try:
        result = db.execute(text("SELECT 1;")).scalar()
        if result == 1:
            raw_version = db.execute(text("SELECT version();")).scalar() or ""
            # Extract clean version without exposing system paths
            short_version = raw_version.split(" on ")[0] if " on " in raw_version else raw_version[:50]
            return {
                "status": "connected",
                "database_engine": "PostgreSQL (Neon)",
                "database_version": short_version,
                "target": get_redacted_database_url(settings.DATABASE_URL or ""),
            }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database did not respond with expected ping result",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {type(e).__name__}",
        )
