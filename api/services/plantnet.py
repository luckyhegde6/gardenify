"""PlantNet API client — species identification and disease detection."""

import logging
from io import BytesIO

import httpx

from api.config import settings

logger = logging.getLogger(__name__)

SPECIES_URL = f"{settings.plantnet_api_url}/identify/all"
DISEASE_URL = f"{settings.plantnet_api_url}/diseases/identify"
VALID_ORGANS = {"leaf", "flower", "fruit", "bark", "auto"}


async def identify_plant(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict:
    """Identify plant species from images via PlantNet API.

    Raises ValueError on invalid input, httpx.HTTPStatusError on API failure.
    """
    if not images:
        raise ValueError("At least one image required")
    if len(images) > settings.max_images:
        raise ValueError(f"Max {settings.max_images} images")

    organs = organs or ["auto"] * len(images)
    if len(organs) != len(images):
        raise ValueError("organs count must match images count")

    bad = [o for o in organs if o not in VALID_ORGANS]
    if bad:
        raise ValueError(f"Invalid organs: {bad}. Use: {VALID_ORGANS}")

    files = [("images", (fn, data.getvalue(), "image/jpeg")) for fn, data in images]

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            SPECIES_URL,
            params={"api-key": settings.plantnet_api_key},
            files=files,
            data={"organs": organs, "lang": lang},
        )

    if resp.status_code == 429:
        logger.warning("PlantNet quota exceeded")
        raise httpx.HTTPStatusError("Quota exceeded", request=resp.request, response=resp)

    resp.raise_for_status()
    return resp.json()


async def identify_disease(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict | None:
    """Detect plant diseases. Returns None on failure (non-critical)."""
    if not images:
        return None

    organs = organs or ["leaf"] * len(images)
    files = [("images", (fn, data.getvalue(), "image/jpeg")) for fn, data in images]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                DISEASE_URL,
                params={"api-key": settings.plantnet_api_key},
                files=files,
                data={"organs": organs, "lang": lang},
            )
        if resp.status_code != 200:
            logger.warning("Disease API returned %s", resp.status_code)
            return None
        return resp.json()
    except Exception as e:
        logger.warning("Disease detection failed: %s", e)
        return None


def parse_species(raw: dict) -> dict:
    """Extract best_match + results[] from PlantNet response."""
    results = []
    for item in raw.get("results", []):
        sp = item.get("species", {})
        results.append({
            "score": item.get("score", 0.0),
            "species": {
                "scientific_name": sp.get("scientificNameWithoutAuthor", ""),
                "common_names": sp.get("commonNames", []),
                "family": sp.get("family", {}).get("scientificNameWithoutAuthor", ""),
                "genus": sp.get("genus", {}).get("scientificNameWithoutAuthor", ""),
            },
        })
    return {
        "best_match": raw.get("bestMatch", ""),
        "results": results,
        "remaining_quota": raw.get("remainingIdentificationRequests"),
        "version": raw.get("version", ""),
    }


def parse_disease(raw: dict | None) -> dict:
    """Extract top disease result. Returns empty dict if nothing found."""
    if not raw or not raw.get("results"):
        return {"name": "", "confidence": 0.0, "description": "", "treatment": ""}
    top = raw["results"][0]
    d = top.get("disease", {})
    return {"name": d.get("name", ""), "confidence": top.get("score", 0.0),
            "description": d.get("description", ""), "treatment": d.get("treatment", "")}
