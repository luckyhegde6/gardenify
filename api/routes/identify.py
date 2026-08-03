"""POST /api/identify — Plant identification with OpenCV gating + DB-first pipeline.

Pipeline:
1. Magic byte + OpenCV validation (reject non-plant images)
2. EXIF/GPS metadata extraction + compression + thumbnails
3. Local perceptual hash DB lookup (gate before PlantNet API call)
4. PlantNet API species + disease identification (only if local has matches)
5. Plant care profile lookup (by genus/family)
"""

import asyncio
import json
import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.config import settings
from api.models.schemas import (
    CareInfo,
    DiseaseResult,
    IdentificationResponse,
    IdentificationResult,
    ImageMetadata,
    OpenCVResult,
    SpeciesInfo,
)
from api.services.cache import (
    cache_get,
    cache_key,
    cache_set,
    compute_hash,
    validate_image,
)
from api.services.image_processor import ImageProcessor
from api.services.plant_care import get_care_profile
from api.services.plantnet import (
    identify_disease,
    identify_plant,
    parse_disease,
    parse_species,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_organs(raw: list[str]) -> list[str]:
    """Handle organs sent as JSON string array (single form field)."""
    if len(raw) == 1 and raw[0].startswith("["):
        try:
            return json.loads(raw[0])
        except (json.JSONDecodeError, TypeError):
            pass
    return raw


@router.post(
    "/identify",
    response_model=IdentificationResponse,
    summary="Identify plant(s) from uploaded images",
    description="""Upload 1-5 plant images (JPEG, PNG, or WebP). The server:
1. Validates via magic bytes + OpenCV edge detection (rejects non-plant images)
2. Extracts EXIF/GPS metadata, compresses, generates thumbnails
3. Searches local perceptual hash DB for visual matches
4. If local DB finds matches → calls PlantNet API for species + disease ID (saves quota)
5. If local DB finds nothing → returns local results only
6. Looks up plant care profile by genus/family

**Organ options:** `auto`, `leaf`, `flower`, `fruit`, `bark`

Returns species match(es) with confidence scores, taxonomy, disease info,
care instructions, and per-image metadata (OpenCV analysis, EXIF, storage paths).
""",
    response_description="Identification results with species matches, disease, care, and image metadata",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["images"],
                        "properties": {
                            "images": {
                                "type": "array",
                                "items": {"type": "string", "format": "binary"},
                                "description": "Plant images (1-5, max 10MB each). Accepted: JPEG, PNG, WebP.",
                            },
                            "organs": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Organ per image: auto, leaf, flower, fruit, bark",
                                "example": ["leaf"],
                            },
                            "lang": {
                                "type": "string",
                                "description": "Response language: en, fr, es",
                                "example": "en",
                            },
                        },
                    },
                }
            }
        }
    },
)
async def identify(
    images: list[UploadFile] = File(
        ...,
        description="Plant images (1-5 files). Accepted formats: JPEG, PNG, WebP. Max 10MB each.",
    ),
    organs: list[str] = Form(
        default=["auto"],
        description="Plant organ per image: auto, leaf, flower, fruit, bark. "
                    "Pass same number as images, or one value applies to all.",
    ),
    lang: str = Form(
        default="en",
        description="Response language code: en (English), fr (French), es (Spanish)",
    ),
):
    """Identify plant + detect disease + return care instructions."""
    organs = _parse_organs(organs)
    _validate_request(images, organs)

    processor = ImageProcessor()
    processed: list[tuple[str, BytesIO]] = []
    hashes: list[str] = []
    meta_list: list[ImageMetadata] = []
    total = 0
    all_plant_like = True

    for i, img in enumerate(images):
        ct = img.content_type or "image/jpeg"
        data = await img.read()
        fn = img.filename or f"img_{i}.jpg"

        try:
            validate_image(fn, len(data), ct)
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
        total += len(data)
        if total > 50 * 1024 * 1024:
            raise HTTPException(400, "Total upload exceeds 50MB")

        pipe = processor.process(data, fn, ct)
        if not pipe.get("valid"):
            raise HTTPException(400, f"OpenCV could not decode image: {fn}")

        ocv = pipe["metadata"].get("opencv", {})
        if not ocv.get("is_plant_like", True):
            all_plant_like = False

        hashes.append(compute_hash(data))
        img_data = pipe.get("compressed_data") or data
        processed.append((fn, BytesIO(img_data)))

        m = pipe["metadata"]
        meta_list.append(ImageMetadata(
            filename=m["filename"],
            size_bytes=m["size_bytes"],
            compressed_size_bytes=m.get("compressed_size_bytes"),
            thumbnail_size_bytes=m.get("thumbnail_size_bytes"),
            compression_ratio=m.get("compression_ratio"),
            width=m.get("width"),
            height=m.get("height"),
            format=m["format"],
            hash_sha256=m["hash_sha256"],
            exif_camera=m.get("exif_camera", ""),
            exif_date_taken=m.get("exif_date_taken", ""),
            gps_latitude=m.get("gps_latitude"),
            gps_longitude=m.get("gps_longitude"),
            exif=m.get("exif", {}),
            opencv=OpenCVResult(**m["opencv"]) if m.get("opencv") else None,
            storage=pipe.get("storage"),
            thumbnail_data_url=pipe.get("thumbnail_data_url", ""),
        ))

    if not all_plant_like:
        raise HTTPException(
            400,
            "Image does not appear to contain a plant. "
            "Try a clearer photo showing a leaf, flower, fruit, or bark.",
        )

    # ── Step 1: Cache check ────────────────────────────────
    key = cache_key(hashes, organs, lang)
    cached = cache_get(key)
    if cached:
        cached["cached"] = True
        return IdentificationResponse(**cached)

    # ── Step 2: Supabase-backed local lookup first (gate before PlantNet) ─
    # Uses the species + image-hash data in Supabase, so it works identically
    # on Vercel and against local Supabase in dev. Skipped cleanly when
    # Supabase is not configured.
    local_results: list[dict] = []
    local_error = None
    from api.services import supabase_species
    if supabase_species.is_available():
        try:
            from api.services.local_identify import local_identify
            local_result = await local_identify(processed, organs)
            local_results = local_result.get("results", [])
        except Exception as e:
            logger.warning("Local identification failed: %s", e)
            local_error = e

    # ── Step 3: Call PlantNet when local DB has no matches ──
    raw = None
    plantnet_error = None
    source = "local"

    has_plantnet = bool(settings.plantnet_api_key)
    local_has_matches = bool(local_results)

    if has_plantnet and not local_has_matches:
        try:
            raw = await asyncio.to_thread(identify_plant, processed, organs)
            source = "plantnet"
        except Exception as e:
            logger.warning("PlantNet API failed after local miss: %s", e)
            plantnet_error = e
    elif has_plantnet and local_has_matches:
        logger.info("Local DB has matches — using local results to save PlantNet quota")
    elif not has_plantnet:
        logger.info("PlantNet API key not configured — using local DB only")

    # ── Step 4: Parse results ───────────────────────────────
    if raw:
        parsed = parse_species(raw)
        results: list[IdentificationResult] = [
            IdentificationResult(score=r["score"], species=SpeciesInfo(**r["species"]))
            for r in parsed["results"]
        ]
    else:
        parsed = {}
        results = [
            IdentificationResult(score=r["score"], species=SpeciesInfo(**r["species"]))
            for r in local_results
        ]
        if not results and local_error:
            logger.error("Both PlantNet and local identification failed")
            raise HTTPException(
                502,
                f"PlantNet={plantnet_error}, local={local_error}",
            ) from local_error

    # ── Step 5: Disease + care (only with PlantNet results) ──
    disease_info, care_info = None, None
    if results and source == "plantnet":
        best = results[0]
        care_info = CareInfo(**get_care_profile(
            best.species.scientific_name, best.species.genus, best.species.family,
        ))
        raw_disease = await asyncio.to_thread(identify_disease, processed, organs)
        if raw_disease:
            disease_info = DiseaseResult(**parse_disease(raw_disease))

    resp_data = {
        "best_match": results[0].species.scientific_name if results else "",
        "results": results,
        "disease": disease_info,
        "care": care_info,
        "metadata": meta_list,
        "remaining_quota": parsed.get("remaining_quota") if raw else None,
        "version": parsed.get("version", "") if raw else "local-1.0",
        "cached": False,
        "identification_id": uuid.uuid4().hex,
        "source": source,
    }
    cache_set(key, resp_data)
    return IdentificationResponse(**resp_data)


def _validate_request(images: list[UploadFile], organs: list[str]):
    if len(images) < 1:
        raise HTTPException(400, "At least 1 image required")
    if len(images) > 5:
        raise HTTPException(400, "Max 5 images")
    if len(organs) != len(images):
        raise HTTPException(400, "organs count must match images")
