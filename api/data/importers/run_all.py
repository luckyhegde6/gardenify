"""Orchestrate all local database imports.

Usage:
    python -m api.data.importers.run_all
    python -m api.data.importers.run_all --seed-only
    python -m api.data.importers.run_all --gbif-only
    python -m api.data.importers.run_all --max-species 5000
"""

import argparse
import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.data.importers.seed_species import seed_database
from api.data.importers.import_gbif import run_import as import_gbif
from api.data.importers.import_plantnet300k import run_import as import_plantnet300k
from api.data.importers.build_hash_index import build_index
from api.services.local_db import get_species_count, get_hash_count

logger = logging.getLogger(__name__)


def run_all(seed_only: bool = False, gbif_only: bool = False,
            max_species: int = 10000) -> dict:
    """Run all import steps.

    Args:
        seed_only: If True, only run seed (skip external datasets).
        gbif_only: If True, only run GBIF import.
        max_species: Max species to import from GBIF.

    Returns:
        Dict with combined stats.
    """
    results = {}

    if not gbif_only:
        # Step 1: Seed database
        logger.info("Step 1: Seeding database with common species...")
        results["seed"] = seed_database()

    if not seed_only:
        # Step 2: Import from GBIF
        logger.info("Step 2: Importing species from GBIF...")
        results["gbif"] = import_gbif(max_species=max_species)

        # Step 3: Import PlantNet-300K metadata (if available)
        logger.info("Step 3: Importing PlantNet-300K metadata...")
        results["plantnet300k"] = import_plantnet300k()

        # Step 4: Build hash index (if images available)
        logger.info("Step 4: Building perceptual hash index...")
        results["hash_index"] = build_index()

    # Final stats
    results["final"] = {
        "total_species": get_species_count(),
        "total_hashes": get_hash_count(),
    }

    logger.info("Import complete: %s", json.dumps(results["final"]))
    return results


def main():
    parser = argparse.ArgumentParser(description="Build local plant database")
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Only seed with common species, skip external datasets",
    )
    parser.add_argument(
        "--gbif-only",
        action="store_true",
        help="Only import from GBIF, skip seed",
    )
    parser.add_argument(
        "--max-species",
        type=int,
        default=10000,
        help="Maximum species to import from GBIF (default: 10000)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )

    results = run_all(
        seed_only=args.seed_only,
        gbif_only=args.gbif_only,
        max_species=args.max_species,
    )
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
