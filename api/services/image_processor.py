"""Image processing pipeline — validation, compression, thumbnails, storage, metadata."""

import base64
import io
import logging
import tempfile
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

DEFAULT_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"


def _resolve_upload_dir() -> Path:
    """Return a writable upload directory.

    Vercel serverless functions have a read-only filesystem except /tmp, so the
    default ``api/data/uploads`` (under /var/task) must fall back to a temp dir.
    """
    try:
        DEFAULT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        probe = DEFAULT_UPLOAD_DIR / ".write_test"
        probe.write_text("ok")
        probe.unlink()
        return DEFAULT_UPLOAD_DIR
    except OSError:
        tmp = Path(tempfile.gettempdir()) / "gardenify-uploads"
        tmp.mkdir(parents=True, exist_ok=True)
        logger.info("Using temp upload dir: %s", tmp)
        return tmp


UPLOAD_DIR = _resolve_upload_dir()

MAGIC_BYTES: dict[str, bytes] = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "image/webp": b"RIFF",
}

THUMBNAIL_SIZE = (256, 256)
MAX_DIM = 2048
COMPRESS_QUALITY = 75


def _ensure_upload_dir(upload_id: str) -> Path:
    """Create per-request upload directory."""
    dirpath = UPLOAD_DIR / upload_id
    dirpath.mkdir(parents=True, exist_ok=True)
    return dirpath


def _cleanup_upload_dir(upload_id: str):
    """Remove upload directory after processing."""
    dirpath = UPLOAD_DIR / upload_id
    try:
        for f in dirpath.iterdir():
            f.unlink()
        dirpath.rmdir()
    except Exception as e:
        logger.warning("Cleanup failed for %s: %s", upload_id, e)


def validate_by_magic(data: bytes, content_type: str) -> bool:
    """Validate image by checking magic bytes."""
    expected = MAGIC_BYTES.get(content_type)
    if not expected:
        return False
    return data[: len(expected)] == expected


def validate_with_opencv(data: bytes) -> dict:
    """Run OpenCV checks: decode, edge detection, content score.

    Returns dict with:
      - valid: bool
      - width, height: int | None
      - edges_detected: int (count of edge pixels)
      - content_score: float (0-1, higher = more structure)
      - is_plant_like: bool (heuristic)
      - mean_color: list[float] BGR
      - dominant_colors: list[dict]
    """
    result = {
        "valid": False,
        "width": None,
        "height": None,
        "edges_detected": 0,
        "total_pixels": 0,
        "content_score": 0.0,
        "is_plant_like": False,
        "mean_color": [0.0, 0.0, 0.0],
        "dominant_colors": [],
    }

    try:
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            logger.warning("OpenCV decode failed")
            return result

        h, w = img.shape[:2]
        result["valid"] = True
        result["width"] = w
        result["height"] = h
        result["total_pixels"] = h * w

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        result["edges_detected"] = int(edges.sum() / 255)
        result["content_score"] = min(1.0, result["edges_detected"] / (h * w * 0.3))

        result["is_plant_like"] = result["content_score"] > 0.01

        mean = cv2.mean(img)[:3]
        result["mean_color"] = [float(mean[0]), float(mean[1]), float(mean[2])]

        pixels = img.reshape(-1, 3)
        if len(pixels) > 0:
            k = min(5, len(pixels))
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            _, _labels, centers = cv2.kmeans(
                pixels.astype(np.float32),
                k,
                None,
                criteria,
                10,
                cv2.KMEANS_RANDOM_CENTERS,
            )
            for center in centers:
                result["dominant_colors"].append({
                    "b": float(center[0]),
                    "g": float(center[1]),
                    "r": float(center[2]),
                })

    except Exception as e:
        logger.warning("OpenCV processing failed: %s", e)

    return result


def compress_image(data: bytes, max_dim: int = MAX_DIM, quality: int = COMPRESS_QUALITY) -> bytes:
    """Compress image: resize if larger than max_dim, reduce JPEG quality."""
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P", "PA"):
            img = img.convert("RGB")
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return buf.getvalue()
    except Exception as e:
        logger.warning("Compression failed: %s", e)
        return data


def generate_thumbnail(data: bytes, size: tuple[int, int] = THUMBNAIL_SIZE) -> bytes:
    """Generate a thumbnail from image data."""
    try:
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P", "PA"):
            img = img.convert("RGB")
        img.thumbnail(size, Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=60, optimize=True)
        return buf.getvalue()
    except Exception as e:
        logger.warning("Thumbnail failed: %s", e)
        return data


def extract_enhanced_metadata(data: bytes, filename: str, content_type: str) -> dict:
    """Extract rich metadata including EXIF, GPS, and format info."""
    from api.services.cache import extract_metadata

    base = extract_metadata(filename, data, content_type)

    try:
        img = Image.open(io.BytesIO(data))
        exif = img.getexif()

        exif_tags = {
            "make": exif.get(271, ""),
            "model": exif.get(272, ""),
            "software": exif.get(305, ""),
            "orientation": exif.get(274, None),
            "xresolution": exif.get(282, None),
            "yresolution": exif.get(283, None),
            "exposure_time": exif.get(33434, ""),
            "fnumber": exif.get(33437, ""),
            "iso": exif.get(34855, None),
            "focal_length": exif.get(37386, ""),
            "flash": exif.get(37385, ""),
            "datetime_original": str(exif.get(36867, "")),
            "datetime_digitized": str(exif.get(36868, "")),
            "offset_time": str(exif.get(36880, "")),
            "offset_time_original": str(exif.get(36881, "")),
            "offset_time_digitized": str(exif.get(36882, "")),
        }

        base["exif"] = {k: (str(v) if v is not None else "") for k, v in exif_tags.items()}
    except Exception as e:
        logger.debug("Enhanced EXIF failed: %s", e)
        base["exif"] = {}

    return base


class ImageProcessor:
    """Complete image processing pipeline."""

    def __init__(self):
        self.upload_id = uuid.uuid4().hex
        self.upload_dir = _ensure_upload_dir(self.upload_id)

    def process(self, data: bytes, filename: str, content_type: str) -> dict:
        """Run full pipeline on a single image.

        Returns:
          {valid, opencv, metadata, compressed_path, thumbnail_path, original_path, ...}
        """
        magic_ok = validate_by_magic(data, content_type)
        if not magic_ok:
            logger.warning("Magic byte validation failed for %s", filename)

        opencv_result = validate_with_opencv(data)

        if not opencv_result["valid"]:
            logger.warning("OpenCV decode failed for %s", filename)
            return {
                "valid": False,
                "error": "OpenCV decode failed",
            }

        compressed = compress_image(data)
        thumbnail = generate_thumbnail(data)
        thumbnail_data_url = (
            f"data:image/jpeg;base64,{base64.b64encode(thumbnail).decode('ascii')}"
        )

        stem = Path(filename).stem or f"img_{uuid.uuid4().hex[:8]}"

        original_path = self.upload_dir / f"{stem}_original.jpg"
        compressed_path = self.upload_dir / f"{stem}_compressed.jpg"
        thumbnail_path = self.upload_dir / f"{stem}_thumb.jpg"

        storage = {}
        try:
            with open(original_path, "wb") as f:
                f.write(data)
            with open(compressed_path, "wb") as f:
                f.write(compressed)
            with open(thumbnail_path, "wb") as f:
                f.write(thumbnail)
            storage = {
                "upload_id": self.upload_id,
                "original": str(original_path),
                "compressed": str(compressed_path),
                "thumbnail": str(thumbnail_path),
            }
        except OSError as e:
            logger.warning("Upload storage write skipped for %s: %s", filename, e)

        meta = extract_enhanced_metadata(data, filename, content_type)
        meta["compressed_size_bytes"] = len(compressed)
        meta["thumbnail_size_bytes"] = len(thumbnail)
        meta["compression_ratio"] = round(len(compressed) / len(data), 3) if data else 0
        meta["opencv"] = opencv_result

        return {
            "valid": True,
            "metadata": meta,
            "compressed_data": compressed,
            "thumbnail_data_url": thumbnail_data_url,
            "storage": storage,
        }

    def get_upload_id(self) -> str:
        return self.upload_id

    def cleanup(self):
        _cleanup_upload_dir(self.upload_id)


def process_uploaded_images(images: list[tuple[bytes, str, str]]) -> dict:
    """Process multiple uploaded images.

    Args:
      images: list of (data, filename, content_type)

    Returns:
      {results: [...], upload_id: str}
    """
    processor = ImageProcessor()
    results = []

    for data, filename, content_type in images:
        result = processor.process(data, filename, content_type)
        results.append(result)

    return {
        "results": results,
        "upload_id": processor.get_upload_id(),
    }
