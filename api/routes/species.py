"""GET /api/species — Search and browse plant species database.

Supabase-backed (works on Vercel and against local Supabase in dev).
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from api.services import supabase_species

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/species",
    summary="Search species database",
    description="Search the plant species database by name, genus, or family. Supports fuzzy matching. Returns count metadata including total species and hash records.",
    response_description="List of matching species with database stats",
)
async def list_species(
    q: str = Query(default="", description="Search query — matches scientific name, common name, genus, or family"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results to return (1-100)"),
):
    """Search species database by name, genus, or family."""
    results = supabase_species.search_species(q, limit) if q else supabase_species.search_species("", limit)
    return {
        "count": len(results),
        "total_species": supabase_species.get_species_count(),
        "total_hashes": supabase_species.get_hash_count(),
        "results": results,
    }


@router.get(
    "/species/{species_id}",
    summary="Get species by ID",
    description="Retrieve full species detail including taxonomy, common names, and reference data using the internal database ID.",
    response_description="Full species detail record",
)
async def get_species(species_id: int):
    """Get species detail by internal database ID."""
    species = supabase_species.get_species_by_id(species_id)
    if not species:
        raise HTTPException(404, f"Species {species_id} not found")
    return species


@router.get(
    "/species/by-name/{scientific_name:path}",
    summary="Get species by scientific name",
    description="Retrieve species detail by exact scientific name (e.g., 'Rosa damascena'). The name is case-sensitive and must match exactly.",
    response_description="Full species detail record",
)
async def get_species_by_name(scientific_name: str):
    """Get species by exact scientific name (case-sensitive)."""
    species = supabase_species.get_species_by_name(scientific_name)
    if not species:
        raise HTTPException(404, f"Species '{scientific_name}' not found")
    return species
