"""Gardenify API — Plant identification backend."""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.routes.health import router as health_router
from api.routes.identify import router as identify_router

# Structured logging: JSON in production, readable in dev
log_level = logging.DEBUG if settings.debug else logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("gardenify")

app = FastAPI(
    title="Gardenify API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
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


app.include_router(health_router, prefix="/api")
app.include_router(identify_router, prefix="/api")

logger.info("Gardenify API started (debug=%s)", settings.debug)
