"""GET /api/species — Search and browse plant species database.

Uses Supabase on Vercel, SQLite locally.
"""

import logging

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter()


def _get_backend():
    """Get the right backend (Supabase or local SQLite)."""
    from api.services import supabase_species
    if supabase_species.is_available():
        return supabase_species
    from api.services import local_db
    return local_db


@router.get("/species")
async def list_species(
    q: str = Query(default="", description="Search by name, genus, or family"),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Search species database."""
    backend = _get_backend()
    if q:
        results = backend.search_species(q, limit)
    else:
        results = backend.search_species("", limit)
    return {
        "count": len(results),
        "total_species": backend.get_species_count(),
        "total_hashes": backend.get_hash_count(),
        "results": results,
    }


@router.get("/species/{species_id}")
async def get_species(species_id: int):
    """Get species detail by ID."""
    backend = _get_backend()
    species = backend.get_species_by_id(species_id)
    if not species:
        raise HTTPException(404, f"Species {species_id} not found")
    return species


@router.get("/species/by-name/{scientific_name:path}")
async def get_species_by_name(scientific_name: str):
    """Get species by exact scientific name."""
    backend = _get_backend()
    species = backend.get_species_by_name(scientific_name)
    if not species:
        raise HTTPException(404, f"Species '{scientific_name}' not found")
    return species
