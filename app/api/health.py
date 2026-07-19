from fastapi import APIRouter
from app.services.scanners.source_registry import SOURCE_REGISTRY

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Standardized live endpoint to verify application stability.
    """
    return {
        "status": "healthy",
        "monitored_sources": list(SOURCE_REGISTRY.keys())
    }
