from datetime import UTC, datetime

from fastapi import APIRouter

from app.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }
