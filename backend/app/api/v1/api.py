
from app.api.v1 import media, albums, memories
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, get_redacted_database_url
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.people import router as people_router
from app.api.v1.employments import router as employments_router
from app.api.v1.educations import router as educations_router
from app.api.v1.families import router as families_router
from app.api.v1.relationships import router as relationships_router
from app.api.v1.relationship_graph import relationships_router as relationships_graph_router
from app.api.v1.relationship_graph import people_router as people_graph_router
from app.api.v1.invitations import router as invitations_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.events import router as events_router
from app.api.v1.activity import router as activity_router
from app.api.v1.profile import router as profile_router
from app.api.v1.search import router as search_router
from app.api.v1.timeline import router as timeline_router

api_router = APIRouter()

# Mount Authentication router (/api/v1/auth)
api_router.include_router(auth_router)

# Mount People router (/api/v1/people)
api_router.include_router(people_router)
api_router.include_router(employments_router)
api_router.include_router(educations_router)
api_router.include_router(people_graph_router)

# Mount Families router (/api/v1/families)
api_router.include_router(families_router)

# Mount Relationships router (/api/v1/relationships)
api_router.include_router(relationships_router)
api_router.include_router(relationships_graph_router)

# Mount Invitations router (/api/v1/invitations)
api_router.include_router(invitations_router)

# Mount Notifications router (/api/v1/notifications)
api_router.include_router(notifications_router)
api_router.include_router(events_router)
api_router.include_router(activity_router)
api_router.include_router(profile_router)
api_router.include_router(search_router)
api_router.include_router(timeline_router)


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

api_router.include_router(media.router, prefix="/media", tags=["media"])
api_router.include_router(albums.router, prefix="/albums", tags=["albums"])
api_router.include_router(memories.router, prefix="/memories", tags=["memories"])
