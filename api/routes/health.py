"""Health check + debug info endpoint."""

import platform
import time
from datetime import UTC, datetime

from fastapi import APIRouter

from api.config import settings
from api.models.schemas import HealthResponse
from api.services.cache import cache_stats

router = APIRouter()
_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check — returns ok + version."""
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/debug")
async def debug_info():
    """Debug endpoint — config, cache stats, environment. Only in dev mode."""
    if not settings.debug:
        return {"detail": "Debug endpoint disabled in production"}

    return {
        "version": "1.0.0",
        "python": platform.python_version(),
        "uptime_seconds": int(time.time() - _start_time),
        "timestamp": datetime.now(UTC).isoformat(),
        "config": {
            "debug": settings.debug,
            "plantnet_configured": bool(settings.plantnet_api_key),
            "supabase_configured": bool(settings.supabase_url),
            "max_images": settings.max_images,
            "cors_origins": settings.cors_origins,
        },
        "cache": cache_stats(),
    }
