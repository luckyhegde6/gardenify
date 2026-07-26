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
from api.services.plantnet import (
    identify_disease,
    identify_plant,
    parse_disease_response,
    parse_plantnet_response,
)
from api.services.plant_care import get_care_profile
from api.services.cache import (
    compute_image_hash,
    extract_image_metadata,
    get_cache_key,
    get_cached_result,
    set_cached_result,
    validate_image,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/identify", response_model=IdentificationResponse)
async def identify(
    images: list[UploadFile] = File(..., description="Plant images (1-5, JPEG/PNG)"),
    organs: list[str] = Form(default=["auto"]),
    lang: str = Form(default="en"),
):
    """Identify a plant species from one or more images.

    Accepts 1-5 images of the same plant. Each image can be tagged with
    an organ type (leaf, flower, fruit, bark, or auto for automatic detection).

    Returns species identification, disease detection, plant care info,
    and image metadata.
    """
    if len(images) < 1:
        raise HTTPException(status_code=400, detail="At least one image is required")

    if len(images) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed")

    if len(organs) != len(images):
        raise HTTPException(
            status_code=400,
            detail="Number of organ labels must match number of images",
        )

    processed_images: list[tuple[str, BytesIO]] = []
    metadata_list: list[ImageMetadata] = []
    image_hashes: list[str] = []
    total_size = 0

    for i, upload_file in enumerate(images):
        content_type = upload_file.content_type or "image/jpeg"
        content = await upload_file.read()
        size = len(content)
        filename = upload_file.filename or f"image_{i}.jpg"

        try:
            validate_image(filename, size, content_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        total_size += size
        max_total = 50 * 1024 * 1024
        if total_size > max_total:
            raise HTTPException(
                status_code=400,
                detail=f"Total image size exceeds {max_total // (1024*1024)}MB limit",
            )

        image_hash = compute_image_hash(content)
        image_hashes.append(image_hash)
        processed_images.append((filename, BytesIO(content)))

        # Extract metadata
        meta = extract_image_metadata(filename, content, content_type, i)
        metadata_list.append(ImageMetadata(**meta))

    # Check cache
    cache_key = get_cache_key(image_hashes, organs, lang)
    cached = get_cached_result(cache_key)
    if cached:
        cached["cached"] = True
        return IdentificationResponse(**cached)

    # Identify species
    try:
        raw_response = await identify_plant(
            images=processed_images,
            organs=organs,
            lang=lang,
        )
    except Exception as e:
        logger.error(f"PlantNet API error: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Plant identification service error: {str(e)}",
        )

    parsed = parse_plantnet_response(raw_response)

    results = []
    for item in parsed["results"]:
        results.append(
            IdentificationResult(
                score=item["score"],
                species=SpeciesInfo(**item["species"]),
            )
        )

    # Get care info for best match
    care_info = None
    disease_info = None
    if results:
        best = results[0]
        care_profile = get_care_profile(
            scientific_name=best.species.scientific_name,
            genus=best.species.genus,
            family=best.species.family,
        )
        care_info = CareInfo(**care_profile)

        # Disease detection (run in parallel conceptually, sequential here)
        disease_raw = await identify_disease(
            images=processed_images,
            organs=organs,
            lang=lang,
        )
        if disease_raw:
            disease_parsed = parse_disease_response(disease_raw)
            disease_info = DiseaseResult(**disease_parsed)

    identification_id = str(uuid.uuid4())

    response_data = {
        "best_match": parsed["best_match"],
        "results": results,
        "disease": disease_info,
        "care": care_info,
        "metadata": metadata_list,
        "remaining_quota": parsed.get("remaining_quota"),
        "version": parsed.get("version", ""),
        "cached": False,
        "identification_id": identification_id,
    }

    # Cache the result
    set_cached_result(cache_key, response_data)

    return IdentificationResponse(**response_data)
