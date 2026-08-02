"""Seed the Supabase species table from the PlantNet GBIF archive.

Downloads and processes the GBIF observation archive on the server (CI) so the
large archive never ships in the Vercel deploy bundle. Upserts unique species
into the Supabase ``species`` table (same schema as ``seed_supabase.py``).

Usage:
    python -m api.data.importers.seed_supabase_gbif
    python -m api.data.importers.seed_supabase_gbif --max-species 20000

Requires ``SUPABASE_URL`` and ``SUPABASE_SERVICE_ROLE_KEY`` env vars.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env.local")

from api.data.importers.import_gbif import (
    download_gbif_archive,
    extract_unique_species,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def _get_client():
    """Build a Supabase client using the service role key (server-side only)."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    from supabase import create_client

    return create_client(url, key)


def _species_rows(species_list: list[dict]) -> list[dict]:
    """Map importer species dicts to Supabase species columns (JSON fields)."""
    rows = []
    for sp in species_list:
        rows.append({
            "scientific_name": sp["scientific_name"],
            "common_names": json.dumps(sp.get("common_names") or []),
            "family": sp.get("family", ""),
            "genus": sp.get("genus", ""),
            "category": sp.get("category", ""),
            "native_regions": json.dumps(sp.get("native_regions") or []),
            "observation_count": sp.get("observation_count", 1),
            "source": sp.get("source", "gbif"),
        })
    return rows


def seed_supabase_gbif(max_species: int = 10000, force_download: bool = False) -> dict:
    """Download GBIF archive to a temp cache, extract species, upsert to Supabase.

    Uses ``api/data/gbif`` as the cache dir (git-ignored) or temp if unavailable.
    Returns a summary dict with insert/update counts.
    """
    client = _get_client()

    try:
        zip_path = download_gbif_archive(force=force_download)
    except Exception as e:
        logger.error("GBIF download failed: %s", e)
        return {"status": "download_failed", "error": str(e)}

    logger.info("Extracting up to %d unique species...", max_species)
    species_list = extract_unique_species(zip_path, max_species=max_species)

    if not species_list:
        logger.warning("No species found in archive")
        return {"status": "no_species_found"}

    rows = _species_rows(species_list)

    inserted = 0
    updated = 0
    errors = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        try:
            existing = (
                client.table("species")
                .select("id, scientific_name, observation_count")
                .in_("scientific_name", [r["scientific_name"] for r in batch])
                .execute()
            )
            existing_by_name = {r["scientific_name"]: r for r in (existing.data or [])}

            to_insert = []
            for row in batch:
                if row["scientific_name"] in existing_by_name:
                    eid = existing_by_name[row["scientific_name"]]["id"]
                    client.table("species").update({
                        "observation_count": (
                            existing_by_name[row["scientific_name"]].get("observation_count", 0)
                            + row["observation_count"]
                        ),
                    }).eq("id", eid).execute()
                    updated += 1
                else:
                    to_insert.append(row)

            if to_insert:
                client.table("species").insert(to_insert).execute()
                inserted += len(to_insert)
        except Exception as e:
            errors += len(batch)
            logger.warning("Batch %d failed: %s", i // BATCH_SIZE, e)

        if (inserted + updated) % 2000 == 0:
            logger.info("Progress: %d inserted, %d updated", inserted, updated)

    logger.info("Seed complete: %d inserted, %d updated, %d errors", inserted, updated, errors)

    return {
        "status": "completed",
        "archive_size_mb": round(zip_path.stat().st_size / (1024 * 1024), 1),
        "species_found": len(species_list),
        "inserted": inserted,
        "updated": updated,
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase species from GBIF")
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

    result = seed_supabase_gbif(
        max_species=args.max_species,
        force_download=args.force_download,
    )
    print(json.dumps(result, indent=2))

    if result.get("status") != "completed":
        sys.exit(1)


if __name__ == "__main__":
    main()
