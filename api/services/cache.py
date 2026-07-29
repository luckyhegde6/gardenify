"""Image hashing, validation, metadata extraction, and result caching."""

import hashlib
import io
import logging
import time

from api.config import settings

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
_CACHE_TTL = 3600  # 1 hour
_cache: dict[str, dict] = {}


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_image(filename: str, size: int, content_type: str) -> None:
    """Raise ValueError if image is invalid."""
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Bad type '{content_type}' — use JPEG/PNG")
    if size == 0:
        raise ValueError(f"'{filename}' is empty")
    max_bytes = settings.max_image_size_mb * 1024 * 1024
    if size > max_bytes:
        raise ValueError(f"'{filename}' exceeds {settings.max_image_size_mb}MB")


def cache_key(hashes: list[str], organs: list[str], lang: str) -> str:
    raw = f"{'|'.join(sorted(hashes))}:{'|'.join(organs)}:{lang}"
    return hashlib.sha256(raw.encode()).hexdigest()


def cache_get(key: str) -> dict | None:
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < _CACHE_TTL:
        logger.debug("Cache HIT %s", key[:12])
        return entry["data"]
    if entry:
        del _cache[key]
    return None


def cache_set(key: str, data: dict) -> None:
    _cache[key] = {"data": data, "ts": time.time()}
    logger.debug("Cache SET %s (size=%d)", key[:12], len(_cache))


def cache_stats() -> dict:
    now = time.time()
    alive = sum(1 for e in _cache.values() if now - e["ts"] < _CACHE_TTL)
    return {"total_entries": len(_cache), "alive_entries": alive, "ttl_seconds": _CACHE_TTL}


def extract_metadata(filename: str, content: bytes, content_type: str) -> dict:
    """Pull dimensions + EXIF from image. Degrades gracefully."""
    from PIL import Image

    meta = {
        "filename": filename,
        "size_bytes": len(content),
        "format": content_type.split("/")[-1].upper(),
        "hash_sha256": compute_hash(content),
        "width": None, "height": None,
        "exif_camera": "", "exif_date_taken": "",
        "gps_latitude": None, "gps_longitude": None,
    }

    try:
        img = Image.open(io.BytesIO(content))
        meta["width"], meta["height"] = img.size

        exif = img.getexif()
        if exif:
            meta["exif_camera"] = str(exif.get(272, ""))
            meta["exif_date_taken"] = str(exif.get(36867, ""))
            gps = exif.get(34853)
            if isinstance(gps, dict) and 2 in gps and 4 in gps:
                lat, lon = gps[2], gps[4]
                if isinstance(lat, (list, tuple)) and len(lat) >= 2:
                    meta["gps_latitude"] = lat[0] + lat[1] / 60
                if isinstance(lon, (list, tuple)) and len(lon) >= 2:
                    meta["gps_longitude"] = lon[0] + lon[1] / 60
    except Exception as e:
        logger.debug("EXIF parse failed for %s: %s", filename, e)

    return meta
