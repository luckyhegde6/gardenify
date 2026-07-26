import logging
import hashlib
from io import BytesIO

from api.config import settings

logger = logging.getLogger(__name__)


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
