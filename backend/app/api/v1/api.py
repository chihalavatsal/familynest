from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational status."""
    return {
        "status": "healthy",
        "app": "FamilyNest API",
        "version": "1.0.0",
        "environment": "development"
    }
