"""Gardenify API — Plant identification backend.

Endpoints:
- /api/identify — Upload plant images for species + disease identification
- /api/history — Retrieve past identification records with image metadata
- /api/species — Browse and search plant species database
- /api/health — Health check and debug info
- /api/admin — User management (admin only)
"""

import logging
import os
import time
import uuid

from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from api.config import settings

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))  # noqa: E402
from api.routes.admin import router as admin_router
from api.routes.health import router as health_router
from api.routes.species import router as species_router

try:
    from api.routes.identify import router as identify_router
    _has_identify = True
except ImportError:
    _has_identify = False

try:
    from api.routes.history import router as history_router
    _has_history = True
except ImportError:
    _has_history = False

log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logger = logging.getLogger("gardenify")

app = FastAPI(
    title="Gardenify API",
    description="Plant identification API with species matching, disease detection, and plant care guidance. Upload plant photos to receive instant identification results with taxonomy, confidence scores, and rich image processing metadata.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Gardenify Support",
        "url": "https://github.com/anomalyco/gardenify",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Service health check and debug information",
        },
        {
            "name": "Identification",
            "description": "Upload plant images for species and disease identification with full image processing pipeline (magic byte validation, OpenCV edge detection, EXIF extraction, compression, thumbnails)",
        },
        {
            "name": "History",
            "description": "Retrieve past identification records with processed image metadata and thumbnails",
        },
        {
            "name": "Species",
            "description": "Browse and search the plant species database by name, genus, or family",
        },
        {
            "name": "Admin",
            "description": "User management endpoints for administrators",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Attach correlation ID, log method/path/status/duration."""
    cid = uuid.uuid4().hex[:8]
    request.state.correlation_id = cid
    start = time.perf_counter()

    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s → %s (%.0fms) [%s]",
        request.method,
        request.url.path,
        response.status_code,
        ms,
        cid,
    )
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Response-Time"] = f"{ms:.0f}ms"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    cid = getattr(request.state, "correlation_id", "?")
    logger.error("Unhandled error [%s]: %s", cid, exc, exc_info=settings.debug)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "correlation_id": cid},
    )


app.include_router(health_router, prefix="/api", tags=["Health"])
if _has_identify:
    app.include_router(identify_router, prefix="/api", tags=["Identification"])
if _has_history:
    app.include_router(history_router, prefix="/api", tags=["History"])
app.include_router(species_router, prefix="/api", tags=["Species"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve the static landing page."""
    from api.landing_page import LANDING_PAGE_HTML
    return HTMLResponse(content=LANDING_PAGE_HTML)


# Initialize local database on startup (skip on Vercel serverless)
if not os.environ.get("VERCEL"):
    try:
        from api.services.local_db import init_db
        init_db()
        from api.data.importers.seed_species import seed_database
        seed_database()
    except Exception as e:
        logger.warning("Local DB init failed: %s", e)

logger.info("Gardenify API started (debug=%s)", settings.debug)
