"""Build perceptual hash index for local plant images.

Scans plantnet-300k images directory, computes dHash for each image,
and stores in the image_hashes table.

Usage:
    python -m api.data.importers.build_hash_index [--images-dir PATH]
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.services.local_db import get_connection, insert_image_hash
from api.services.perceptual_hash import compute_dhash

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def build_index(images_dir: str | Path | None = None) -> dict:
    """Build perceptual hash index for all images.

    Args:
        images_dir: Path to images directory. If None, uses default.

    Returns:
        Dict with build stats.
    """
    if images_dir:
        images_dir = Path(images_dir)
    else:
        images_dir = PROJECT_ROOT / "api" / "data" / "plantnet-300k" / "images"

    if not images_dir.exists():
        return {
            "status": "skipped",
            "reason": f"Images directory not found: {images_dir}",
            "hint": "Download PlantNet-300K from Zenodo first",
        }

    # Collect all image files
    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(images_dir.rglob(f"*{ext}"))
        image_files.extend(images_dir.rglob(f"*{ext.upper()}"))

    if not image_files:
        return {
            "status": "skipped",
            "reason": f"No images found in {images_dir}",
        }

    logger.info("Found %d images to index", len(image_files))

    conn = get_connection()
    try:
        # Get species mapping from directory structure
        species_map = _build_species_map(conn, images_dir)

        indexed = 0
        errors = 0
        for img_path in image_files:
            try:
                data = img_path.read_bytes()
                dhash = compute_dhash(data)

                # Determine species from path
                species_id = _get_species_from_path(species_map, img_path, images_dir)

                if species_id:
                    relative_path = str(img_path.relative_to(images_dir))
                    insert_image_hash(
                        species_id=species_id,
                        image_path=relative_path,
                        phash=dhash,
                        dhash=dhash,
                        category=_get_category_from_path(img_path, images_dir),
                    )
                    indexed += 1
                else:
                    errors += 1

            except Exception as e:
                logger.warning("Failed to hash %s: %s", img_path, e)
                errors += 1

            if (indexed + errors) % 1000 == 0:
                logger.info("Progress: %d indexed, %d errors", indexed, errors)

    finally:
        conn.close()

    logger.info("Hash index built: %d indexed, %d errors", indexed, errors)
    return {
        "status": "completed",
        "indexed": indexed,
        "errors": errors,
        "total_images": len(image_files),
    }


def _build_species_map(conn, images_dir: Path) -> dict[str, int]:
    """Build mapping of species names to IDs from directory structure."""
    rows = conn.execute("SELECT id, scientific_name FROM species").fetchall()
    # Normalize names for path matching
    return {
        row["scientific_name"].lower().replace(" ", "_"): row["id"]
        for row in rows
    }


def _get_species_from_path(species_map: dict, img_path: Path,
                           images_dir: Path) -> int | None:
    """Extract species ID from image file path.

    Expected structure: images/category/species_name/image.jpg
    """
    try:
        relative = img_path.relative_to(images_dir)
        parts = relative.parts
        if len(parts) >= 2:
            # parts[0] = category, parts[1] = species_name
            species_key = parts[1].lower()
            return species_map.get(species_key)
    except ValueError:
        pass
    return None


def _get_category_from_path(img_path: Path, images_dir: Path) -> str:
    """Extract category from image file path."""
    try:
        relative = img_path.relative_to(images_dir)
        parts = relative.parts
        if len(parts) >= 1:
            return parts[0]
    except ValueError:
        pass
    return ""


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = build_index()
    print(json.dumps(result, indent=2))
