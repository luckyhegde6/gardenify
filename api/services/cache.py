import hashlib
import logging
import time
from io import BytesIO

from api.config import settings

logger = logging.getLogger(__name__)

# In-memory cache for identification results (production: use Redis/Supabase)
_result_cache: dict[str, dict] = {}
_CACHE_TTL_SECONDS = 3600  # 1 hour


def compute_image_hash(image_bytes: bytes) -> str:
    """Compute SHA-256 hash of image bytes for deduplication.

    Args:
        image_bytes: Raw image binary data.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    return hashlib.sha256(image_bytes).hexdigest()


def validate_image(filename: str, size: int, content_type: str) -> None:
    """Validate image before processing.

    Args:
        filename: Original filename.
        size: File size in bytes.
        content_type: MIME type of the file.

    Raises:
        ValueError: If image fails validation.
    """
    allowed_types = {"image/jpeg", "image/png", "image/jpg"}
    if content_type not in allowed_types:
        raise ValueError(
            f"Invalid image type '{content_type}'. "
            f"Allowed: {', '.join(allowed_types)}"
        )

    max_size = settings.max_image_size_mb * 1024 * 1024
    if size > max_size:
        raise ValueError(
            f"Image '{filename}' exceeds maximum size of "
            f"{settings.max_image_size_mb}MB ({size} bytes)"
        )

    if size == 0:
        raise ValueError(f"Image '{filename}' is empty")


def get_cache_key(hashes: list[str], organs: list[str], lang: str) -> str:
    """Generate a cache key from image hashes and request params.

    Args:
        hashes: List of image SHA-256 hashes.
        organs: List of organ types.
        lang: Language code.

    Returns:
        Cache key string.
    """
    key_data = f"{'|'.join(sorted(hashes))}:{'|'.join(organs)}:{lang}"
    return hashlib.sha256(key_data.encode()).hexdigest()


def get_cached_result(cache_key: str) -> dict | None:
    """Look up a cached identification result.

    Args:
        cache_key: The cache key to look up.

    Returns:
        Cached result dict if found and not expired, else None.
    """
    if cache_key in _result_cache:
        entry = _result_cache[cache_key]
        if time.time() - entry["timestamp"] < _CACHE_TTL_SECONDS:
            logger.info(f"Cache HIT for key {cache_key[:12]}...")
            return entry["result"]
        else:
            del _result_cache[cache_key]
            logger.info(f"Cache EXPIRED for key {cache_key[:12]}...")

    return None


def set_cached_result(cache_key: str, result: dict) -> None:
    """Store an identification result in cache.

    Args:
        cache_key: The cache key.
        result: The result dict to cache.
    """
    _result_cache[cache_key] = {
        "result": result,
        "timestamp": time.time(),
    }
    logger.info(f"Cached result for key {cache_key[:12]}... (total: {len(_result_cache)})")


def clear_expired_cache() -> int:
    """Remove expired entries from cache.

    Returns:
        Number of entries removed.
    """
    now = time.time()
    expired = [
        key for key, entry in _result_cache.items()
        if now - entry["timestamp"] >= _CACHE_TTL_SECONDS
    ]
    for key in expired:
        del _result_cache[key]
    return len(expired)


def extract_image_metadata(
    filename: str,
    content: bytes,
    content_type: str,
    index: int,
) -> dict:
    """Extract metadata from an uploaded image.

    Args:
        filename: Original filename.
        content: Raw image bytes.
        content_type: MIME type.
        index: Image index in the upload batch.

    Returns:
        Dict with metadata fields.
    """
    from PIL import Image
    import io

    metadata = {
        "filename": filename,
        "size_bytes": len(content),
        "format": content_type.split("/")[-1].upper(),
        "hash_sha256": compute_image_hash(content),
        "width": None,
        "height": None,
        "exif_camera": "",
        "exif_date_taken": "",
        "gps_latitude": None,
        "gps_longitude": None,
    }

    try:
        img = Image.open(io.BytesIO(content))
        metadata["width"] = img.width
        metadata["height"] = img.height

        # Extract EXIF data if available
        exif_data = img.getexif() if hasattr(img, "getexif") else None
        if exif_data:
            # Camera model (tag 272)
            if 272 in exif_data:
                metadata["exif_camera"] = str(exif_data[272])

            # Date taken (tag 36867)
            if 36867 in exif_data:
                metadata["exif_date_taken"] = str(exif_data[36867])

            # GPS info (tag 34853)
            if 34853 in exif_data:
                gps = exif_data[34853]
                if isinstance(gps, dict):
                    # Simplified GPS extraction
                    if 2 in gps and 4 in gps:
                        lat = gps[2]
                        lon = gps[4]
                        if isinstance(lat, (list, tuple)) and len(lat) >= 2:
                            metadata["gps_latitude"] = lat[0] + lat[1] / 60
                        if isinstance(lon, (list, tuple)) and len(lon) >= 2:
                            metadata["gps_longitude"] = lon[0] + lon[1] / 60

    except Exception as e:
        logger.warning(f"Could not extract metadata from {filename}: {e}")

    return metadata
