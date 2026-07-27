"""POST /api/identify — Plant identification, disease detection, care analysis."""

import logging
import uuid
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models.schemas import (
    CareInfo,
    DiseaseResult,
    IdentificationResponse,
    IdentificationResult,
    ImageMetadata,
    SpeciesInfo,
)
from api.services.cache import (
    cache_get,
    cache_key,
    cache_set,
    compute_hash,
    extract_metadata,
    validate_image,
)
from api.services.plant_care import get_care_profile
from api.services.plantnet import (
    identify_disease,
    identify_plant,
    parse_disease,
    parse_species,
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

    # Species identification — try PlantNet API first, fall back to local DB
    raw = None
    plantnet_error = None
    source = "plantnet"
    try:
        raw = await identify_plant(processed, organs, lang)
    except Exception as e:
        logger.warning("PlantNet API failed, trying local DB: %s", e)
        plantnet_error = e
        source = "local"

    if raw:
        parsed = parse_species(raw)
        results = [
            IdentificationResult(score=r["score"], species=SpeciesInfo(**r["species"]))
            for r in parsed["results"]
        ]
    else:
        # Offline fallback — local perceptual hash matching
        parsed = {}
        try:
            from api.services.local_identify import local_identify
            local_result = await local_identify(processed, organs)
            results = [
                IdentificationResult(score=r["score"], species=SpeciesInfo(**r["species"]))
                for r in local_result.get("results", [])
            ]
            source = "local"
        except Exception as local_err:
            logger.error("Local identification also failed: %s", local_err)
            raise HTTPException(
                502,
                f"Identification failed: PlantNet={plantnet_error}, local={local_err}",
            ) from local_err

    # Disease + care (only if we got a match, and only with PlantNet API)
    disease_info, care_info = None, None
    if results and source == "plantnet":
        best = results[0]
        care_info = CareInfo(**get_care_profile(
            best.species.scientific_name, best.species.genus, best.species.family,
        ))
        raw_disease = await identify_disease(processed, organs, lang)
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
