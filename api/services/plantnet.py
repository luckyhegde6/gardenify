"""PlantNet API client — species identification and disease detection."""

import json
import logging
import uuid
from io import BytesIO
from urllib.request import Request, urlopen

from api.config import settings

logger = logging.getLogger(__name__)

SPECIES_URL = f"{settings.plantnet_api_url}/identify/all"
DISEASE_URL = f"{settings.plantnet_api_url}/diseases/identify"
VALID_ORGANS = {"leaf", "flower", "fruit", "bark", "auto"}


def _build_multipart(
    images: list[tuple[str, BytesIO]],
    organs: list[str],
) -> tuple[bytes, str]:
    """Build multipart/form-data body and boundary.

    PlantNet API v2 does NOT accept a ``lang`` parameter.
    Must repeat ``organs`` field per image (one value or same for all).
    """
    boundary = uuid.uuid4().hex
    body = bytearray()

    for fn, data in images:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="images"; filename="{fn}"\r\n'.encode())
        body.extend(b"Content-Type: image/jpeg\r\n\r\n")
        body.extend(data.getvalue())
        body.extend(b"\r\n")

    for organ in organs:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(b'Content-Disposition: form-data; name="organs"\r\n\r\n')
        body.extend(organ.encode())
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), boundary


def _call_plantnet(url: str, images: list[tuple[str, BytesIO]], organs: list[str]) -> dict:
    """Call PlantNet API via urllib with multipart body.

    Note: PlantNet API v2 does NOT accept a ``lang`` parameter.
    """
    body, boundary = _build_multipart(images, organs)
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}

    req = Request(url, data=body, headers=headers, method="POST")
    try:
        resp = urlopen(req, timeout=30)
    except Exception as e:
        logger.warning("PlantNet request failed: %s", e)
        raise RuntimeError(str(e)) from e

    raw = json.loads(resp.read())
    logger.debug("PlantNet response keys=%s, results=%d",
                  list(raw.keys()), len(raw.get("results", [])))
    return raw


def identify_plant(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict:
    """Identify plant species from images via PlantNet API.

    Raises ValueError on invalid input, RuntimeError on API failure.
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

    url = f"{SPECIES_URL}?api-key={settings.plantnet_api_key}"
    data = _call_plantnet(url, images, organs)

    quota = data.get("remainingIdentificationRequests")
    if quota is not None and quota == 0:
        logger.warning("PlantNet daily quota exhausted")
        raise RuntimeError("Quota exhausted")

    return data


def identify_disease(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
    lang: str = "en",
) -> dict | None:
    """Detect plant diseases. Returns None on failure (non-critical)."""
    if not images:
        return None

    organs = organs or ["leaf"] * len(images)
    try:
        url = f"{DISEASE_URL}?api-key={settings.plantnet_api_key}"
        data = _call_plantnet(url, images, organs)
        return data
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
