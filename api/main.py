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
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.config import settings

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.local"))
from api.routes.admin import router as admin_router
from api.routes.auth import router as auth_router
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
    version="1.1.0",
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
            "name": "Auth",
            "description": "Login (rate-limited) and password recovery endpoints",
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
app.include_router(auth_router, prefix="/api", tags=["Auth"])
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



@app.get("/about", response_class=HTMLResponse)
async def about_page():
    """About page linking to GitHub profile and contribution guide."""
    from api.landing_page import ABOUT_PAGE_HTML
    return HTMLResponse(content=ABOUT_PAGE_HTML)




@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page():
    """Onboarding page with architecture, workflows, and sequence diagrams."""
    from api.onboarding_page import ONBOARDING_PAGE_HTML
    return HTMLResponse(content=ONBOARDING_PAGE_HTML)


FAVICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "images" / "favicon.png"
BASE_URL = "https://sasyakashi.vercel.app"
SITEMAP_URLS = ["/", "/about", "/onboarding", "/docs", "/redoc", "/api/health"]


@app.get("/favicon.png", include_in_schema=False)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve the app favicon (avoids 404 for browser requests)."""
    data = FAVICON_PATH.read_bytes()
    return Response(content=data, media_type="image/png")


@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    """Generate an XML sitemap of the public pages (avoids 404 for crawlers)."""
    urls = "".join(
        f"    <url><loc>{BASE_URL}{path}</loc></url>\n" for path in SITEMAP_URLS
    )
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return a branded HTML 404 for unknown non-API paths, JSON for API paths."""
    if exc.status_code == 404:
        if request.url.path.startswith("/api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found"})
        from api.landing_page import NOT_FOUND_HTML
        return HTMLResponse(content=NOT_FOUND_HTML, status_code=404)
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc.detail)})


logger.info("Gardenify API started (debug=%s)", settings.debug)
