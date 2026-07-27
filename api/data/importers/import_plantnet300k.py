"""Import PlantNet-300K metadata into local SQLite database.

Reads metadata JSON files and populates the species table.
Can work with or without actual images (metadata-only import).

Usage:
    python -m api.data.importers.import_plantnet300k [--metadata-dir PATH]
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.services.local_db import get_connection, init_db, insert_species

logger = logging.getLogger(__name__)

# Default metadata files (can be downloaded from Seafile)
METADATA_FILES = {
    "species_names": "plantnet300K_species_id_2_name.json",
    "metadata": "plantnet300K_metadata.json",
    "class_idx": "class_idx_to_species_id.json",
}

# PlantNet-300K categories
CATEGORIES = [
    "woody_plant",
    "herbaceous_flowering_plant",
    "fungus",
    "fern",
    "moss_liverwort",
    "succulent",
    "grass",
    "fern_allies",
]


def import_species_names(metadata_dir: Path) -> dict[str, str]:
    """Import species ID to name mapping.

    Returns dict of species_id -> scientific_name.
    """
    species_file = metadata_dir / METADATA_FILES["species_names"]
    if not species_file.exists():
        logger.warning("Species names file not found: %s", species_file)
        return {}

    with open(species_file, encoding="utf-8") as f:
        data = json.load(f)

    logger.info("Loaded %d species names", len(data))
    return data


def import_metadata(metadata_dir: Path) -> dict:
    """Import full metadata file.

    Returns metadata dict keyed by image ID.
    """
    meta_file = metadata_dir / METADATA_FILES["metadata"]
    if not meta_file.exists():
        logger.warning("Metadata file not found: %s", meta_file)
        return {}

    with open(meta_file, encoding="utf-8") as f:
        data = json.load(f)

    logger.info("Loaded metadata for %d images", len(data))
    return data


def populate_species(species_names: dict[str, str], metadata: dict) -> int:
    """Populate species table from metadata.

    Returns count of species inserted.
    """
    init_db()

    # Group metadata by species
    species_obs: dict[str, dict] = {}

    for img_id, img_meta in metadata.items():
        species_id = img_meta.get("species_id", "")
        if not species_id or species_id not in species_names:
            continue

        sci_name = species_names[species_id]
        if sci_name not in species_obs:
            species_obs[sci_name] = {
                "scientific_name": sci_name,
                "common_names": "[]",
                "family": "",
                "genus": sci_name.split()[0] if " " in sci_name else "",
                "category": _guess_category(img_meta),
                "native_regions": "[]",
                "observation_count": 0,
                "source": "plantnet300k",
            }
        species_obs[sci_name]["observation_count"] += 1

    count = 0
    for sci_name, data in species_obs.items():
        insert_species(data)
        count += 1

    logger.info("Imported %d species from PlantNet-300K metadata", count)
    return count


def _guess_category(img_meta: dict) -> str:
    """Try to guess category from metadata fields."""
    # PlantNet-300K doesn't always have category in metadata
    # Return empty string if unknown
    return ""


def run_import(metadata_dir: str | Path | None = None) -> dict:
    """Run full PlantNet-300K metadata import.

    Args:
        metadata_dir: Path to directory containing metadata JSON files.
                     If None, uses default location.

    Returns:
        Dict with import stats.
    """
    if metadata_dir:
        metadata_dir = Path(metadata_dir)
    else:
        metadata_dir = PROJECT_ROOT / "api" / "data" / "plantnet-300k" / "metadata"

    logger.info("Starting PlantNet-300K import from %s", metadata_dir)

    species_names = import_species_names(metadata_dir)
    metadata = import_metadata(metadata_dir)

    if not species_names:
        return {
            "status": "skipped",
            "reason": "No metadata files found. Download from Seafile first.",
            "download_url": "https://lab.plantnet.org/seafile/d/bed81bc15e8944969cf6/",
            "species_count": 0,
        }

    count = populate_species(species_names, metadata)

    return {
        "status": "completed",
        "species_count": count,
        "metadata_dir": str(metadata_dir),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_import()
    print(json.dumps(result, indent=2))
