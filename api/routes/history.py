"""GET /api/history — Retrieve past identification records.

Supports Supabase-backed storage for authenticated users.
Returns processed image details including thumbnail paths and metadata.
"""

import logging
import os

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from api.models.schemas import (
    HistoryDetailResponse,
    HistoryListResponse,
    HistoryRecord,
    IdentificationResult,
    SpeciesInfo,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def _get_user_id(authorization: str | None = None) -> str:
    """Extract user ID from JWT via Supabase."""
    from supabase import create_client

    from api.config import settings

    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(503, "Supabase not configured")

    token = authorization.removeprefix("Bearer ")
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    try:
        user_resp = client.auth.get_user(token)
        return user_resp.user.id
    except Exception as e:
        raise HTTPException(401, f"Invalid token: {e}") from e


@router.get(
    "/history",
    response_model=HistoryListResponse,
    summary="List past identifications",
    description="""Retrieve paginated identification history for the authenticated user.

Requires a valid Supabase JWT in the Authorization header.

Returns species matches, confidence scores, thumbnail URLs, and timestamps.
Results are ordered by most recent first.
""",
    response_description="Paginated list of identification history records",
)
async def list_history(
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
):
    """List identification history for authenticated user.

    Requires Supabase JWT in Authorization header.
    """
    from supabase import create_client

    from api.config import settings

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(503, "Supabase not configured")

    client = create_client(settings.supabase_url, settings.supabase_anon_key)

    query = (
        client.table("identifications")
        .select("*", count="exact")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    try:
        resp = query.execute()
    except Exception as e:
        raise HTTPException(502, f"Database query failed: {e}") from e

    total = resp.count or 0
    records = []
    for row in resp.data or []:
        records.append(HistoryRecord(
            id=row.get("id", ""),
            best_match=row.get("best_match", ""),
            score=row.get("score", 0.0),
            species_scientific_name=row.get("species_scientific_name", ""),
            species_common_names=row.get("species_common_names", []),
            species_family=row.get("species_family", ""),
            species_genus=row.get("species_genus", ""),
            image_urls=row.get("image_urls", []),
            thumbnail_urls=row.get("thumbnail_urls", []),
            organs=row.get("organs", []),
            source=row.get("source", ""),
            created_at=str(row.get("created_at", "")),
        ))

    return HistoryListResponse(records=records, total=total)


@router.get(
    "/history/{identification_id}",
    response_model=HistoryDetailResponse,
    summary="Get identification detail",
    description="Retrieve full identification result including species matches, disease detection, care instructions, and per-image processing metadata.",
    response_description="Complete identification result with all analysis data",
)
async def get_history_detail(identification_id: str):
    """Get full identification detail by ID."""
    from supabase import create_client

    from api.config import settings

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(503, "Supabase not configured")

    client = create_client(settings.supabase_url, settings.supabase_anon_key)

    try:
        resp = (
            client.table("identifications")
            .select("*")
            .eq("id", identification_id)
            .maybe_single()
            .execute()
        )
    except Exception as e:
        raise HTTPException(502, f"Database query failed: {e}") from e

    if not resp.data:
        raise HTTPException(404, "Identification not found")

    row = resp.data
    import json

    results_json = row.get("results_json", "{}")
    if isinstance(results_json, str):
        parsed = json.loads(results_json)
    else:
        parsed = results_json or {}

    results = [
        IdentificationResult(
            score=r.get("score", 0.0),
            species=SpeciesInfo(**r.get("species", {})),
        )
        for r in parsed.get("results", [])
    ]

    from api.models.schemas import CareInfo, DiseaseResult, ImageMetadata

    disease = None
    if parsed.get("disease"):
        disease = DiseaseResult(**parsed["disease"])

    care = None
    if parsed.get("care"):
        care = CareInfo(**parsed["care"])

    meta_list = []
    for m in parsed.get("metadata", []):
        meta_list.append(ImageMetadata(**m))

    return HistoryDetailResponse(
        id=row.get("id", ""),
        best_match=row.get("best_match", ""),
        results=results,
        disease=disease,
        care=care,
        metadata=meta_list,
        source=row.get("source", ""),
        created_at=str(row.get("created_at", "")),
    )


@router.get(
    "/history/{identification_id}/thumbnail/{image_index}",
    summary="Serve thumbnail image",
    description="Returns the processed thumbnail image (256x256 JPEG) for a specific image in an identification record.",
    response_description="JPEG thumbnail image",
    response_class=FileResponse,
)
async def serve_thumbnail(identification_id: str, image_index: int):
    """Serve a processed thumbnail image from upload storage."""
    from supabase import create_client

    from api.config import settings

    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(503, "Supabase not configured")

    client = create_client(settings.supabase_url, settings.supabase_anon_key)

    try:
        resp = (
            client.table("identifications")
            .select("results_json")
            .eq("id", identification_id)
            .maybe_single()
            .execute()
        )
    except Exception as e:
        raise HTTPException(502, f"Database query failed: {e}") from e

    if not resp.data:
        raise HTTPException(404, "Identification not found")

    import json

    results_json = resp.data.get("results_json", "{}")
    if isinstance(results_json, str):
        parsed = json.loads(results_json)
    else:
        parsed = results_json or {}

    meta_list = parsed.get("metadata", [])
    if image_index >= len(meta_list):
        raise HTTPException(404, f"Image index {image_index} out of range")

    storage = meta_list[image_index].get("storage", {})
    thumb_path = storage.get("thumbnail", "")
    if not thumb_path or not os.path.isfile(thumb_path):
        raise HTTPException(404, "Thumbnail not found on server")

    return FileResponse(thumb_path, media_type="image/jpeg")
