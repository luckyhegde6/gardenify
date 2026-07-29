"""Health check and debug endpoints."""

import os
import sys
import time

from fastapi import APIRouter

from api.config import settings

_start_time = time.time()

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Returns API status and version. Use for load balancer health checks and monitoring.",
    response_description="Status object with version info",
)
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "ok", "version": "1.0.0"}


@router.get(
    "/debug",
    summary="Debug information",
    description="Returns configuration and system information for debugging. Includes Python version, uptime, and feature flags.",
    response_description="Debug info with config, uptime, and feature availability",
)
async def debug_info():
    """Debug endpoint returning config and system info."""
    from api.services.cache import cache_stats
    return {
        "version": "1.0.0",
        "python": sys.version.split()[0],
        "uptime_seconds": int(time.time() - _start_time),
        "cache": cache_stats(),
        "config": {
            "debug": settings.debug,
            "environment": settings.environment,
            "use_remote": settings.use_remote,
            "plantnet_configured": bool(settings.plantnet_api_key),
            "supabase_configured": bool(settings.supabase_url and settings.supabase_anon_key),
            "max_images": settings.max_images,
            "max_image_size_mb": settings.max_image_size_mb,
        },
    }
