"""Build perceptual hash index from GBIF/PlantNet image URLs into Supabase.

Pipeline:
1. Read species from Supabase
2. Match against GBIF multimedia URLs (bs.plantnet.org)
3. Download one representative image per species
4. Compute pHash + dHash
5. Store in Supabase image_hashes table
6. Cache images locally in api/data/hashes/{species_id}/

Usage:
    python scripts/build_hash_index.py [--limit 100] [--force]
"""

import argparse
import csv
import io
import json
import logging
import os
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env.local")

from api.services.perceptual_hash import compute_dhash, compute_phash
from api.services.supabase_species import get_species_images, insert_image_hash

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("build_hash_index")

GBIF_ZIP = PROJECT_ROOT / "api" / "data" / "gbif" / "plantnet_observations.zip"
HASHES_DIR = PROJECT_ROOT / "api" / "data" / "hashes"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
TIMEOUT = 15
DELAY = 0.5  # seconds between downloads (rate limiting)
BATCH_SIZE = 200


def _get_client():
    """Build a Supabase client using the service role key (server-side only)."""
    from supabase import create_client

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

    return create_client(url, key)


def load_species_from_db() -> dict[str, int]:
    """Return {scientific_name_lower: id} for all species in Supabase."""
    client = _get_client()
    rows = (
        client.table("species")
        .select("id, scientific_name")
        .order("id")
        .execute()
    )
    return {r["scientific_name"].strip().lower(): r["id"] for r in (rows.data or [])}


_AUTHOR_RE = re.compile(
    r"(\s+\([^)]*\))?\s+[A-Z][a-zäëïöü]*(?:\s+et\s+[A-Z][a-z]+)?(?:\s+[A-Z]\.)?(?:\s+ex\s+[A-Z][a-z]+)?(?:\s+f\.)?(?:\s+[A-Z]\.)?\s*$"
)


def _clean_name(gbif_name: str) -> str:
    """Strip author citation from GBIF scientific name.

    'Daucus carota L.' → 'daucus carota'
    'Ipomoea pandurata (L.) G. Mey.' → 'ipomoea pandurata'
    'Echinocystis lobata (Michx.) Torr. & A.Gray' → 'echinocystis lobata'
    """
    name = _AUTHOR_RE.sub("", gbif_name).strip().lower()
    # Also handle ampersand patterns sometimes left
    name = re.sub(r"\s+&\s+\w+(?:\.\w+)?$", "", name).strip()
    return name


def build_gbif_image_index() -> dict[str, dict]:
    """Build {cleaned_species_name: {url, part}} from GBIF multimedia."""
    if not GBIF_ZIP.exists():
        logger.warning("GBIF zip not found: %s", GBIF_ZIP)
        return {}

    z = zipfile.ZipFile(str(GBIF_ZIP))
    index: dict[str, dict] = {}
    total = 0

    with z.open("multimedia.txt") as f:
        reader = csv.DictReader(
            io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t"
        )
        for row in reader:
            total += 1
            raw = row.get("scientificName", "").strip()
            url = row.get("accessURI", "").strip()
            part = row.get("subjectPart", "auto").strip().lower()
            if not raw or not url:
                continue
            cleaned = _clean_name(raw)
            if not cleaned:
                continue
            if cleaned not in index:
                index[cleaned] = {"url": url, "part": part or "auto", "raw": raw}
            elif index[cleaned].get("part", "auto") == "auto" and part != "auto":
                index[cleaned] = {"url": url, "part": part, "raw": raw}

    z.close()
    logger.info("GBIF entries: %d, unique species: %d", total, len(index))
    return index


def download_image(url: str, max_bytes: int = 5 * 1024 * 1024) -> bytes | None:
    """Download image from URL with size limit and timeout."""
    try:
        req = Request(url, headers={"User-Agent": "Gardenify/1.0"})
        with urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                logger.warning("Image too large (%d bytes): %s", len(data), url)
                return None
            return data
    except Exception as e:
        logger.debug("Download failed: %s — %s", url, e)
        return None


def build_index(limit: int | None = None, force: bool = False) -> dict:
    """Build hash index from GBIF image URLs into Supabase."""
    results = {"species_in_db": 0, "matched_gbif": 0, "downloaded": 0, "indexed": 0, "errors": 0, "skipped": 0}

    species_map = load_species_from_db()
    results["species_in_db"] = len(species_map)
    logger.info("Loaded %d species from Supabase", len(species_map))

    gbif_index = build_gbif_image_index()
    results["matched_gbif"] = len(gbif_index)
    logger.info("GBIF multimedia index: %d entries", len(gbif_index))

    HASHES_DIR.mkdir(parents=True, exist_ok=True)

    # Find intersection: species that exist in both DB and GBIF
    candidates = []
    for name, sid in species_map.items():
        if name in gbif_index:
            candidates.append((sid, name, gbif_index[name]))

    logger.info("Species with GBIF images: %d", len(candidates))

    if limit:
        candidates = candidates[:limit]

    for sid, name, info in candidates:
        species_dir = HASHES_DIR / str(sid)
        species_dir.mkdir(exist_ok=True)

        url = info["url"]
        part = info["part"]

        # Skip if already has hashes (unless force)
        existing = get_species_images(sid)
        if not force and existing:
            results["skipped"] += 1
            continue

        # Check if image already cached
        cached = None
        for f in species_dir.iterdir():
            if f.suffix.lower() in IMAGE_EXTS:
                cached = f
                break

        if cached:
            data = cached.read_bytes()
            logger.info("Using cached: %s", cached.name)
        else:
            data = download_image(url)
            if not data:
                results["errors"] += 1
                continue

            # Save to cache
            ext = Path(url.split("?")[0]).suffix or ".jpg"
            cache_path = species_dir / f"img{ext}"
            cache_path.write_bytes(data)
            logger.info("Downloaded: %s → %s (%d bytes)", name, cache_path.name, len(data))

        # Compute hashes
        try:
            phash = compute_phash(data)
            dhash = compute_dhash(data)
        except Exception as e:
            logger.warning("Hash failed for species %d: %s", sid, e)
            results["errors"] += 1
            continue

        # Store in Supabase
        rel_path = str(species_dir.relative_to(HASHES_DIR) / (cached.name if cached else f"img{Path(url.split('?')[0]).suffix or '.jpg'}"))
        if insert_image_hash(
            species_id=sid,
            image_path=rel_path,
            phash=phash,
            dhash=dhash,
            category=part,
        ):
            results["indexed"] += 1
        else:
            results["errors"] += 1
            continue
        results["downloaded"] += 0 if cached else 1

        time.sleep(DELAY)

    logger.info(
        "Done: %d indexed, %d errors, %d skipped (from %d candidates)",
        results["indexed"], results["errors"], results["skipped"], len(candidates),
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build perceptual hash index")
    parser.add_argument("--limit", type=int, default=None, help="Max species to process")
    parser.add_argument("--force", action="store_true", help="Re-hash even if already indexed")
    args = parser.parse_args()

    result = build_index(limit=args.limit, force=args.force)
    print(json.dumps(result, indent=2))
