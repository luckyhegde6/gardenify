"""POST /api/identify — Plant identification, disease detection, care analysis."""

import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models.schemas import (
    CareInfo, DiseaseResult, IdentificationResponse,
    IdentificationResult, ImageMetadata, SpeciesInfo,
)
from api.services.plantnet import identify_plant, identify_disease, parse_species, parse_disease
from api.services.plant_care import get_care_profile
from api.services.cache import (
    compute_hash, validate_image, cache_key, cache_get, cache_set, extract_metadata,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/identify", response_model=IdentificationResponse)
async def identify(
    images: list[UploadFile] = File(..., description="Plant images (1-5, JPEG/PNG)"),
    organs: list[str] = Form(default=["auto"]),
    lang: str = Form(default="en"),
):
    """Identify plant + detect disease + return care instructions."""
    _validate_request(images, organs)

    # Process images: validate, hash, extract metadata
    processed: list[tuple[str, BytesIO]] = []
    hashes, meta_list = [], []
    total = 0

    for i, img in enumerate(images):
        ct = img.content_type or "image/jpeg"
        data = await img.read()
        fn = img.filename or f"img_{i}.jpg"

        validate_image(fn, len(data), ct)
        total += len(data)
        if total > 50 * 1024 * 1024:
            raise HTTPException(400, "Total upload exceeds 50MB")

        hashes.append(compute_hash(data))
        processed.append((fn, BytesIO(data)))
        meta_list.append(ImageMetadata(**extract_metadata(fn, data, ct)))

    # Cache check
    key = cache_key(hashes, organs, lang)
    cached = cache_get(key)
    if cached:
        cached["cached"] = True
        return IdentificationResponse(**cached)

    # Species identification
    try:
        raw = await identify_plant(processed, organs, lang)
    except Exception as e:
        logger.error("PlantNet error: %s", e)
        raise HTTPException(502, f"Identification failed: {e}")

    parsed = parse_species(raw)
    results = [
        IdentificationResult(score=r["score"], species=SpeciesInfo(**r["species"]))
        for r in parsed["results"]
    ]

    # Disease + care (only if we got a match)
    disease_info, care_info = None, None
    if results:
        best = results[0]
        care_info = CareInfo(**get_care_profile(
            best.species.scientific_name, best.species.genus, best.species.family,
        ))
        raw_disease = await identify_disease(processed, organs, lang)
        if raw_disease:
            disease_info = DiseaseResult(**parse_disease(raw_disease))

    resp_data = {
        "best_match": parsed["best_match"],
        "results": results,
        "disease": disease_info,
        "care": care_info,
        "metadata": meta_list,
        "remaining_quota": parsed.get("remaining_quota"),
        "version": parsed.get("version", ""),
        "cached": False,
        "identification_id": uuid.uuid4().hex,
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
