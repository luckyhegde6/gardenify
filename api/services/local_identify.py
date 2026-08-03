"""Local plant identification — species search and visual matching.

Uses Supabase for species data + perceptual hashes, so it works identically
on Vercel and against local Supabase in dev. Returns the same structure as
PlantNet API for compatibility.
"""

import logging
from io import BytesIO

from api.services.perceptual_hash import compute_phash
from api.services.supabase_species import (
    find_by_phash,
    get_species_by_id,
    get_species_by_name,
    search_species,
)

logger = logging.getLogger(__name__)


async def local_identify(
    images: list[tuple[str, BytesIO]],
    organs: list[str] | None = None,
) -> dict:
    """Identify plants using Supabase-backed species database.

    Tries perceptual hash matching first, falls back to empty results.
    Returns same structure as PlantNet API for compatibility.
    """
    results = []

    for fn, data in images:
        data_bytes = data.getvalue()
        if not data_bytes:
            continue

        # Compute hashes
        try:
            phash = compute_phash(data_bytes)
        except Exception as e:
            logger.warning("Hash computation failed for %s: %s", fn, e)
            continue

        # Search by hash
        matches = find_by_phash(phash, max_distance=12)
        if matches:
            for match in matches[:3]:
                results.append({
                    "score": max(0.0, 1.0 - (match.get("hamming_dist", 0) / 64.0)),
                    "species": {
                        "scientific_name": match.get("scientific_name", ""),
                        "common_names": match.get("common_names", []),
                        "family": match.get("family", ""),
                        "genus": match.get("genus", ""),
                    },
                    "match_type": "visual",
                    "hamming_distance": match.get("hamming_dist", 0),
                })

    # Deduplicate by scientific name
    seen = set()
    unique = []
    for r in results:
        name = r["species"]["scientific_name"]
        if name not in seen:
            seen.add(name)
            unique.append(r)

    # Sort by score descending
    unique.sort(key=lambda x: x["score"], reverse=True)

    best_match = unique[0]["species"]["scientific_name"] if unique else ""

    return {
        "best_match": best_match,
        "results": unique,
        "disease": None,
        "care": None,
        "metadata": [],
        "remaining_quota": None,
        "version": "local-1.0",
        "cached": False,
        "identification_id": None,
        "source": "local",
    }


def search_local_species(query: str, limit: int = 20) -> list[dict]:
    """Search species in Supabase."""
    return search_species(query, limit)


def get_local_species_detail(species_id: int) -> dict | None:
    """Get full species detail from Supabase."""
    return get_species_by_id(species_id)


def get_local_species_by_name(scientific_name: str) -> dict | None:
    """Get species by exact scientific name from Supabase."""
    return get_species_by_name(scientific_name)
