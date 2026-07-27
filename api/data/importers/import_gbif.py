"""Import unique species from PlantNet GBIF Darwin Core Archive.

Downloads the observation dataset from GBIF and extracts unique species
with taxonomy data. This populates the local database with real species
information without needing images.

Usage:
    python -m api.data.importers.import_gbif
    python -m api.data.importers.import_gbif --max-species 5000
"""

import argparse
import csv
import json
import logging
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.services.local_db import get_connection, init_db, insert_species

logger = logging.getLogger(__name__)

# PlantNet observations dataset on GBIF IPT
GBIF_URL = "https://ipt.plantnet.org/archive.do?r=observations"
GBIF_CACHE_DIR = Path(__file__).parent.parent / "gbif"

# Darwin Core Archive contains these files
# We need: observations.csv (main data), taxons.csv (taxonomy)
CORE_FILE = "observations.csv"
TAXON_FILE = "taxons.csv"


def download_gbif_archive(force: bool = False) -> Path:
    """Download the PlantNet GBIF Darwin Core Archive.

    Returns path to the downloaded zip file.
    """
    GBIF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = GBIF_CACHE_DIR / "plantnet_observations.zip"

    if zip_path.exists() and not force:
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        logger.info("Archive already downloaded: %.1f MB at %s", size_mb, zip_path)
        return zip_path

    logger.info("Downloading PlantNet GBIF archive from %s ...", GBIF_URL)
    logger.info("This may take several minutes (~500MB-2GB)")

    response = requests.get(GBIF_URL, stream=True, timeout=600)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0 and downloaded % (10 * 1024 * 1024) < 8192:
                pct = (downloaded / total) * 100
                logger.info("Downloaded: %.1f MB / %.1f MB (%.1f%%)",
                           downloaded / (1024 * 1024),
                           total / (1024 * 1024), pct)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    logger.info("Download complete: %.1f MB", size_mb)
    return zip_path


def extract_and_analyze(zip_path: Path) -> dict:
    """Extract Darwin Core Archive and analyze contents.

    Returns dict with file names and row counts.
    """
    logger.info("Extracting archive...")
    analysis = {}

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        logger.info("Archive contains %d files:", len(names))
        for name in names:
            info = zf.getinfo(name)
            size_mb = info.file_size / (1024 * 1024)
            logger.info("  %s (%.1f MB)", name, size_mb)

        # Extract to temp dir for analysis
        extract_dir = GBIF_CACHE_DIR / "extracted"
        extract_dir.mkdir(exist_ok=True)
        zf.extractall(extract_dir)

    # Count rows in key files
    for name in names:
        fpath = extract_dir / name
        if fpath.exists() and fpath.suffix == ".csv":
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for _ in reader) - 1  # minus header
                    analysis[name] = {"rows": row_count, "path": str(fpath)}
                    logger.info("  %s: %d rows", name, row_count)
            except Exception as e:
                logger.warning("  Could not read %s: %s", name, e)

    return analysis


def extract_unique_species(zip_path: Path, max_species: int = 10000) -> list[dict]:
    """Extract unique species from the Darwin Core Archive.

    Reads the occurrence.txt file (tab-separated) and extracts unique
    species with observation counts.

    Args:
        zip_path: Path to the downloaded zip file
        max_species: Maximum number of species to import

    Returns:
        List of species dicts ready for insert_species()
    """
    species_map = {}  # scientific_name -> species dict

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        logger.info("Archive contains files: %s", names)

        # Find the occurrence file (tab-separated)
        obs_file = None
        for name in names:
            if name.lower().endswith(".txt") and "occurrence" in name.lower():
                obs_file = name
                break

        if not obs_file:
            logger.error("No occurrence file found in archive")
            return []

        logger.info("Reading occurrences from %s...", obs_file)
        with zf.open(obs_file) as f:
            data = f.read().decode("utf-8", errors="replace")
            lines = data.split("\n")

            if not lines:
                return []

            # Parse header to find column indices
            header = lines[0].split("\t")
            logger.info("Columns: %s", header[:10])

            # Find scientificName column
            sci_col = None
            for i, col in enumerate(header):
                if col.lower() == "scientificname":
                    sci_col = i
                    break

            if sci_col is None:
                logger.error("No scientificName column found")
                return []

            logger.info("scientificName is at column index %d", sci_col)

            # Count unique species
            for line in lines[1:]:
                if not line.strip():
                    continue

                cols = line.split("\t")
                if len(cols) <= sci_col:
                    continue

                sci_name = cols[sci_col].strip()
                if not sci_name or sci_name.lower() in ("", "unknown"):
                    continue

                # Remove author name (everything after the second space)
                # "Monstera deliciosa Liebm." -> "Monstera deliciosa"
                parts = sci_name.split()
                if len(parts) >= 2:
                    clean_name = f"{parts[0]} {parts[1]}"
                else:
                    clean_name = sci_name

                if clean_name not in species_map:
                    # Extract genus from scientific name
                    genus = parts[0] if parts else ""

                    species_map[clean_name] = {
                        "scientific_name": clean_name,
                        "common_names": "[]",
                        "family": "",
                        "genus": genus,
                        "category": "",
                        "native_regions": "[]",
                        "observation_count": 0,
                        "source": "gbif",
                    }

                species_map[clean_name]["observation_count"] += 1

                if len(species_map) % 1000 == 0:
                    logger.info("Found %d unique species so far...", len(species_map))

                if len(species_map) >= max_species:
                    break

    logger.info("Total unique species found: %d", len(species_map))
    return list(species_map.values())


def import_to_database(species_list: list[dict]) -> dict:
    """Import species list into the local SQLite database.

    Args:
        species_list: List of species dicts

    Returns:
        Dict with import stats
    """
    init_db()
    conn = get_connection()

    inserted = 0
    updated = 0
    errors = 0

    try:
        for species in species_list:
            try:
                existing = conn.execute(
                    "SELECT id FROM species WHERE scientific_name = ?",
                    (species["scientific_name"],),
                ).fetchone()

                if existing:
                    conn.execute(
                        """UPDATE species SET
                            observation_count = observation_count + ?
                           WHERE id = ?""",
                        (species["observation_count"], existing["id"]),
                    )
                    updated += 1
                else:
                    conn.execute(
                        """INSERT INTO species
                            (scientific_name, common_names, family, genus,
                             category, native_regions, observation_count, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            species["scientific_name"],
                            species["common_names"],
                            species["family"],
                            species["genus"],
                            species["category"],
                            species["native_regions"],
                            species["observation_count"],
                            species["source"],
                        ),
                    )
                    inserted += 1

                if (inserted + updated) % 1000 == 0:
                    conn.commit()
                    logger.info("Progress: %d inserted, %d updated", inserted, updated)

            except Exception as e:
                errors += 1
                logger.warning("Error importing %s: %s",
                              species.get("scientific_name", "?"), e)

        conn.commit()
    finally:
        conn.close()

    return {
        "inserted": inserted,
        "updated": updated,
        "errors": errors,
        "total_processed": inserted + updated + errors,
    }


def run_import(max_species: int = 10000, force_download: bool = False) -> dict:
    """Run the full GBIF import pipeline.

    Args:
        max_species: Maximum species to import
        force_download: Force re-download even if archive exists

    Returns:
        Dict with import stats
    """
    logger.info("=== GBIF Import Pipeline ===")

    # Step 1: Download archive
    logger.info("Step 1: Downloading GBIF archive...")
    try:
        zip_path = download_gbif_archive(force=force_download)
    except requests.RequestException as e:
        logger.error("Download failed: %s", e)
        return {"status": "download_failed", "error": str(e)}

    # Step 2: Extract unique species
    logger.info("Step 2: Extracting unique species...")
    species_list = extract_unique_species(zip_path, max_species=max_species)

    if not species_list:
        logger.warning("No species found in archive")
        return {"status": "no_species_found"}

    # Step 3: Import to database
    logger.info("Step 3: Importing %d species to database...", len(species_list))
    import_stats = import_to_database(species_list)

    logger.info("=== Import Complete ===")
    logger.info("Inserted: %d", import_stats["inserted"])
    logger.info("Updated: %d", import_stats["updated"])
    logger.info("Errors: %d", import_stats["errors"])

    return {
        "status": "completed",
        "archive_size_mb": zip_path.stat().st_size / (1024 * 1024),
        "species_found": len(species_list),
        **import_stats,
    }


def main():
    parser = argparse.ArgumentParser(description="Import species from GBIF")
    parser.add_argument(
        "--max-species", type=int, default=10000,
        help="Maximum species to import (default: 10000)",
    )
    parser.add_argument(
        "--force-download", action="store_true",
        help="Force re-download even if archive exists",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )

    result = run_import(
        max_species=args.max_species,
        force_download=args.force_download,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
