import logging
from io import BytesIO

import httpx

from api.config import settings

logger = logging.getLogger(__name__)

PLANTNET_IDENTIFY_URL = f"{settings.plantnet_api_url}/identify/all"
PLANTNET_DISEASE_URL = f"{settings.plantnet_api_url}/diseases/identify"


async def identify_plant(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict:
    """Identify a plant species from one or more images.

    Args:
        images: List of (filename, image_bytes) tuples.
        organs: Organ type per image (leaf/flower/fruit/bark/auto).
        lang: Response language code.

    Returns:
        PlantNet API response dict.

    Raises:
        httpx.HTTPStatusError: If PlantNet returns an error.
        ValueError: If input validation fails.
    """
    if not images:
        raise ValueError("At least one image is required")

    if len(images) > settings.max_images:
        raise ValueError(f"Maximum {settings.max_images} images allowed")

    if organs is None:
        organs = ["auto"] * len(images)

    if len(organs) != len(images):
        raise ValueError("Number of organs must match number of images")

    valid_organs = {"leaf", "flower", "fruit", "bark", "auto"}
    for organ in organs:
        if organ not in valid_organs:
            raise ValueError(f"Invalid organ '{organ}'. Must be one of: {valid_organs}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        files = []
        for filename, image_bytes in images:
            files.append(("images", (filename, image_bytes.getvalue(), "image/jpeg")))

        data = {"organs": organs, "lang": lang}

        response = await client.post(
            PLANTNET_IDENTIFY_URL,
            params={"api-key": settings.plantnet_api_key},
            files=files,
            data=data,
        )

        if response.status_code == 429:
            logger.warning("PlantNet quota exceeded")
            raise httpx.HTTPStatusError(
                "Daily identification quota exceeded",
                request=response.request,
                response=response,
            )

        response.raise_for_status()
        return response.json()


async def identify_disease(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict | None:
    """Identify plant diseases from images using PlantNet diseases API.

    Args:
        images: List of (filename, image_bytes) tuples.
        organs: Organ type per image.
        lang: Response language code.

    Returns:
        Disease identification response dict, or None if unavailable.
    """
    if not images:
        return None

    if organs is None:
        organs = ["leaf"] * len(images)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = []
            for filename, image_bytes in images:
                files.append(("images", (filename, image_bytes.getvalue(), "image/jpeg")))

            data = {"organs": organs, "lang": lang}

            response = await client.post(
                PLANTNET_DISEASE_URL,
                params={"api-key": settings.plantnet_api_key},
                files=files,
                data=data,
            )

            if response.status_code != 200:
                logger.warning(f"Disease API returned status {response.status_code}")
                return None

            return response.json()

    except Exception as e:
        logger.warning(f"Disease identification failed: {e}")
        return None


def parse_plantnet_response(raw: dict) -> dict:
    """Parse PlantNet API response into our standardized format.

    Args:
        raw: Raw PlantNet API response.

    Returns:
        Parsed response with best_match, results, and metadata.
    """
    results = []
    for item in raw.get("results", []):
        species = item.get("species", {})
        results.append({
            "score": item.get("score", 0.0),
            "species": {
                "scientific_name": species.get("scientificNameWithoutAuthor", ""),
                "common_names": species.get("commonNames", []),
                "family": species.get("family", {}).get("scientificNameWithoutAuthor", ""),
                "genus": species.get("genus", {}).get("scientificNameWithoutAuthor", ""),
            },
        })

    return {
        "best_match": raw.get("bestMatch", ""),
        "results": results,
        "remaining_quota": raw.get("remainingIdentificationRequests"),
        "version": raw.get("version", ""),
    }


def parse_disease_response(raw: dict) -> dict:
    """Parse PlantNet disease API response.

    Args:
        raw: Raw PlantNet disease API response.

    Returns:
        Parsed disease result.
    """
    if not raw or "results" not in raw or not raw["results"]:
        return {"name": "", "confidence": 0.0, "description": "", "treatment": ""}

    top = raw["results"][0]
    return {
        "name": top.get("disease", {}).get("name", ""),
        "confidence": top.get("score", 0.0),
        "description": top.get("disease", {}).get("description", ""),
        "treatment": top.get("disease", {}).get("treatment", ""),
    }
