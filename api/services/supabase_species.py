"""Supabase-backed species search and detail.

Used on Vercel where SQLite is not available.
Falls back gracefully if Supabase is not configured.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

_supabase_client = None


def _get_client():
    """Get Supabase client (lazy init)."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        logger.warning("Supabase client init failed: %s", e)
        return None


def is_available() -> bool:
    """Check if Supabase is configured."""
    return _get_client() is not None


def search_species(query: str, limit: int = 20) -> list[dict]:
    """Search species via Supabase.

    Uses RPC for full search including JSONB common_names,
    falls back to text-only PostgREST filter if RPC not available.
    """
    client = _get_client()
    if not client:
        return []

    if not query:
        query = ""

    try:
        resp = (
            client.table("species")
            .select("id, scientific_name, common_names, family, genus, category, native_regions, observation_count")
            .or_(
                f"scientific_name.ilike.%{query}%,"
                f"genus.ilike.%{query}%,"
                f"family.ilike.%{query}%"
            )
            .order("observation_count", desc=True)
            .limit(limit)
            .execute()
        )
        results = [_row_to_dict(r) for r in (resp.data or [])]

        if query and len(results) < limit:
            seen_ids = {r["id"] for r in results}
            all_resp = (
                client.table("species")
                .select("id, scientific_name, common_names, family, genus, category, native_regions, observation_count")
                .order("observation_count", desc=True)
                .execute()
            )
            q_lower = query.lower()
            for row in (all_resp.data or []):
                if row["id"] in seen_ids:
                    continue
                cn = row.get("common_names", [])
                if isinstance(cn, str):
                    try:
                        cn = json.loads(cn)
                    except (json.JSONDecodeError, TypeError):
                        cn = []
                if any(q_lower in name.lower() for name in cn):
                    results.append(_row_to_dict(row))
                    seen_ids.add(row["id"])
                if len(results) >= limit:
                    break

        return results[:limit]
    except Exception as e:
        logger.error("Supabase search failed: %s", e)
        return []


def get_species_by_id(species_id: int) -> dict | None:
    """Get species detail by ID from Supabase."""
    client = _get_client()
    if not client:
        return None

    try:
        resp = (
            client.table("species")
            .select("*")
            .eq("id", species_id)
            .execute()
        )
        if not resp.data:
            return None
        result = _row_to_dict(resp.data[0])
        # Ensure images key exists for API contract parity with local_db
        if "images" not in result:
            result["images"] = []
        return result
    except Exception as e:
        logger.error("Supabase get by ID failed: %s", e)
        return None


def get_species_by_name(scientific_name: str) -> dict | None:
    """Get species by exact scientific name from Supabase."""
    client = _get_client()
    if not client:
        return None

    try:
        resp = (
            client.table("species")
            .select("*")
            .eq("scientific_name", scientific_name)
            .execute()
        )
        if not resp.data:
            return None
        return _row_to_dict(resp.data[0])
    except Exception as e:
        logger.error("Supabase get by name failed: %s", e)
        return None


def get_species_count() -> int:
    """Get total species count from Supabase."""
    client = _get_client()
    if not client:
        return 0

    try:
        resp = client.table("species").select("id", count="exact").execute()
        return resp.count or 0
    except Exception:
        return 0


def get_hash_count() -> int:
    """Image hashes not stored in Supabase (only in local SQLite)."""
    return 0


def insert_species(species_data: dict) -> int | None:
    """Insert or update a species in Supabase."""
    client = _get_client()
    if not client:
        return None

    try:
        # Check if exists
        resp = (
            client.table("species")
            .select("id")
            .eq("scientific_name", species_data["scientific_name"])
            .execute()
        )

        if resp.data:
            # Update
            existing_id = resp.data[0]["id"]
            client.table("species").update({
                "observation_count": (
                    client.table("species")
                    .select("observation_count")
                    .eq("id", existing_id)
                    .execute()
                    .data[0]["observation_count"]
                    + species_data.get("observation_count", 1)
                ),
            }).eq("id", existing_id).execute()
            return existing_id

        # Insert
        resp = (
            client.table("species")
            .insert({
                "scientific_name": species_data["scientific_name"],
                "common_names": species_data.get("common_names", "[]"),
                "family": species_data.get("family", ""),
                "genus": species_data.get("genus", ""),
                "category": species_data.get("category", ""),
                "native_regions": species_data.get("native_regions", "[]"),
                "observation_count": species_data.get("observation_count", 1),
                "source": species_data.get("source", "manual"),
            })
            .execute()
        )
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        logger.error("Supabase insert failed: %s", e)
        return None


def _row_to_dict(row: dict) -> dict:
    """Convert Supabase row to dict, parsing JSON fields."""
    for key in ("common_names", "native_regions"):
        if key in row and isinstance(row[key], str):
            try:
                row[key] = json.loads(row[key])
            except (json.JSONDecodeError, TypeError):
                row[key] = []
        elif key in row and isinstance(row[key], list):
            pass  # Already parsed
    return row
