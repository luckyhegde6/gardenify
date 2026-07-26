import logging
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models.schemas import IdentificationResponse, IdentificationResult, SpeciesInfo
from api.services.plantnet import identify_plant, parse_plantnet_response
from api.services.cache import compute_image_hash, validate_image

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
        processed_images.append((filename, BytesIO(content)))

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

    return IdentificationResponse(
        best_match=parsed["best_match"],
        results=results,
        remaining_quota=parsed.get("remaining_quota"),
        version=parsed.get("version", ""),
    )
