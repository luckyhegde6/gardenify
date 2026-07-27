"""Seed Supabase with common plant species.

Run this once to populate the production database:
    python -m api.data.importers.seed_supabase
"""

import json
import logging
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env.local")

logger = logging.getLogger(__name__)


# Common species — same as seed_species.py
SEED_SPECIES = [
    {"scientific_name": "Monstera deliciosa", "common_names": ["Swiss Cheese Plant", "Split-leaf Philodendron"], "family": "Araceae", "genus": "Monstera", "category": "herbaceous_flowering_plant", "native_regions": ["Central America"], "observation_count": 150},
    {"scientific_name": "Ficus benjamina", "common_names": ["Weeping Fig", "Ficus Tree"], "family": "Moraceae", "genus": "Ficus", "category": "woody_plant", "native_regions": ["Southeast Asia"], "observation_count": 120},
    {"scientific_name": "Echeveria elegans", "common_names": ["Mexican Snowball", "Echeveria"], "family": "Crassulaceae", "genus": "Echeveria", "category": "succulent", "native_regions": ["Mexico"], "observation_count": 95},
    {"scientific_name": "Ocimum basilicum", "common_names": ["Sweet Basil", "Basil"], "family": "Lamiaceae", "genus": "Ocimum", "category": "herbaceous_flowering_plant", "native_regions": ["India", "Southeast Asia"], "observation_count": 200},
    {"scientific_name": "Rosa damascena", "common_names": ["Damask Rose", "Rose"], "family": "Rosaceae", "genus": "Rosa", "category": "woody_plant", "native_regions": ["Middle East"], "observation_count": 180},
    {"scientific_name": "Quercus robur", "common_names": ["English Oak", "Pedunculate Oak"], "family": "Fagaceae", "genus": "Quercus", "category": "woody_plant", "native_regions": ["Europe"], "observation_count": 300},
    {"scientific_name": "Helianthus annuus", "common_names": ["Common Sunflower", "Sunflower"], "family": "Asteraceae", "genus": "Helianthus", "category": "herbaceous_flowering_plant", "native_regions": ["North America"], "observation_count": 250},
    {"scientific_name": "Nephrolepis exaltata", "common_names": ["Boston Fern", "Sword Fern"], "family": "Nephrolepidaceae", "genus": "Nephrolepis", "category": "fern", "native_regions": ["Tropics"], "observation_count": 85},
    {"scientific_name": "Aloe vera", "common_names": ["Aloe Vera", "Burn Plant"], "family": "Asphodelaceae", "genus": "Aloe", "category": "succulent", "native_regions": ["Arabian Peninsula"], "observation_count": 175},
    {"scientific_name": "Acer palmatum", "common_names": ["Japanese Maple", "Momiji"], "family": "Sapindaceae", "genus": "Acer", "category": "woody_plant", "native_regions": ["Japan", "Korea", "China"], "observation_count": 140},
    {"scientific_name": "Epipremnum aureum", "common_names": ["Devil's Ivy", "Golden Pothos"], "family": "Araceae", "genus": "Epipremnum", "category": "herbaceous_flowering_plant", "native_regions": ["Southeast Asia"], "observation_count": 160},
    {"scientific_name": "Lavandula angustifolia", "common_names": ["English Lavender", "Lavender"], "family": "Lamiaceae", "genus": "Lavandula", "category": "herbaceous_flowering_plant", "native_regions": ["Mediterranean"], "observation_count": 190},
    {"scientific_name": "Mentha spicata", "common_names": ["Spearmint", "Mint"], "family": "Lamiaceae", "genus": "Mentha", "category": "herbaceous_flowering_plant", "native_regions": ["Europe", "Asia"], "observation_count": 170},
    {"scientific_name": "Spathiphyllum wallisii", "common_names": ["Peace Lily", "White Sails"], "family": "Araceae", "genus": "Spathiphyllum", "category": "herbaceous_flowering_plant", "native_regions": ["Central America"], "observation_count": 130},
    {"scientific_name": "Crassula ovata", "common_names": ["Jade Plant", "Money Tree"], "family": "Crassulaceae", "genus": "Crassula", "category": "succulent", "native_regions": ["South Africa"], "observation_count": 145},
    {"scientific_name": "Dracaena marginata", "common_names": ["Dragon Tree", "Madagascar Dragon Tree"], "family": "Asparagaceae", "genus": "Dracaena", "category": "herbaceous_flowering_plant", "native_regions": ["Madagascar"], "observation_count": 105},
    {"scientific_name": "Phalaenopsis amabilis", "common_names": ["Moth Orchid", "Orchid"], "family": "Orchidaceae", "genus": "Phalaenopsis", "category": "herbaceous_flowering_plant", "native_regions": ["Southeast Asia"], "observation_count": 155},
    {"scientific_name": "Sansevieria trifasciata", "common_names": ["Snake Plant", "Mother-in-Law's Tongue"], "family": "Asparagaceae", "genus": "Dracaena", "category": "herbaceous_flowering_plant", "native_regions": ["West Africa"], "observation_count": 165},
    {"scientific_name": "Zamioculcas zamiifolia", "common_names": ["ZZ Plant", "Zanzibar Gem"], "family": "Araceae", "genus": "Zamioculcas", "category": "herbaceous_flowering_plant", "native_regions": ["East Africa"], "observation_count": 100},
    {"scientific_name": "Ficus elastica", "common_names": ["Rubber Plant", "Rubber Fig"], "family": "Moraceae", "genus": "Ficus", "category": "woody_plant", "native_regions": ["Southeast Asia"], "observation_count": 135},
]


def seed_supabase():
    """Seed the Supabase species table."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        return

    from supabase import create_client
    client = create_client(url, key)

    inserted = 0
    updated = 0

    for sp in SEED_SPECIES:
        try:
            # Check if exists
            resp = (
                client.table("species")
                .select("id")
                .eq("scientific_name", sp["scientific_name"])
                .execute()
            )

            if resp.data:
                # Update count
                client.table("species").update({
                    "observation_count": sp["observation_count"],
                }).eq("id", resp.data[0]["id"]).execute()
                updated += 1
            else:
                # Insert
                client.table("species").insert({
                    "scientific_name": sp["scientific_name"],
                    "common_names": json.dumps(sp["common_names"]),
                    "family": sp["family"],
                    "genus": sp["genus"],
                    "category": sp["category"],
                    "native_regions": json.dumps(sp["native_regions"]),
                    "observation_count": sp["observation_count"],
                    "source": "seed",
                }).execute()
                inserted += 1

        except Exception as e:
            logger.error("Failed to seed %s: %s", sp["scientific_name"], e)

    logger.info("Seeded Supabase: %d inserted, %d updated", inserted, updated)
    print(f"Done: {inserted} inserted, {updated} updated")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_supabase()
