"""Seed the local database with common plant species for testing.

Creates a starter dataset so the API works without downloading
large external datasets. Can be extended with real data later.
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.services.local_db import get_connection, init_db, insert_species

logger = logging.getLogger(__name__)

# Common species with basic taxonomy — enough for testing
SEED_SPECIES = [
    {
        "scientific_name": "Monstera deliciosa",
        "common_names": json.dumps(["Swiss Cheese Plant", "Split-leaf Philodendron"]),
        "family": "Araceae",
        "genus": "Monstera",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Central America"]),
        "observation_count": 150,
        "source": "seed",
    },
    {
        "scientific_name": "Ficus benjamina",
        "common_names": json.dumps(["Weeping Fig", "Ficus Tree"]),
        "family": "Moraceae",
        "genus": "Ficus",
        "category": "woody_plant",
        "native_regions": json.dumps(["Southeast Asia"]),
        "observation_count": 120,
        "source": "seed",
    },
    {
        "scientific_name": "Echeveria elegans",
        "common_names": json.dumps(["Mexican Snowball", "Echeveria"]),
        "family": "Crassulaceae",
        "genus": "Echeveria",
        "category": "succulent",
        "native_regions": json.dumps(["Mexico"]),
        "observation_count": 95,
        "source": "seed",
    },
    {
        "scientific_name": "Ocimum basilicum",
        "common_names": json.dumps(["Sweet Basil", "Basil"]),
        "family": "Lamiaceae",
        "genus": "Ocimum",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["India", "Southeast Asia"]),
        "observation_count": 200,
        "source": "seed",
    },
    {
        "scientific_name": "Rosa damascena",
        "common_names": json.dumps(["Damask Rose", "Rose"]),
        "family": "Rosaceae",
        "genus": "Rosa",
        "category": "woody_plant",
        "native_regions": json.dumps(["Middle East"]),
        "observation_count": 180,
        "source": "seed",
    },
    {
        "scientific_name": "Quercus robur",
        "common_names": json.dumps(["English Oak", "Pedunculate Oak"]),
        "family": "Fagaceae",
        "genus": "Quercus",
        "category": "woody_plant",
        "native_regions": json.dumps(["Europe"]),
        "observation_count": 300,
        "source": "seed",
    },
    {
        "scientific_name": "Helianthus annuus",
        "common_names": json.dumps(["Common Sunflower", "Sunflower"]),
        "family": "Asteraceae",
        "genus": "Helianthus",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["North America"]),
        "observation_count": 250,
        "source": "seed",
    },
    {
        "scientific_name": "Nephrolepis exaltata",
        "common_names": json.dumps(["Boston Fern", "Sword Fern"]),
        "family": "Nephrolepidaceae",
        "genus": "Nephrolepis",
        "category": "fern",
        "native_regions": json.dumps(["Tropics"]),
        "observation_count": 85,
        "source": "seed",
    },
    {
        "scientific_name": "Aloe vera",
        "common_names": json.dumps(["Aloe Vera", "Burn Plant"]),
        "family": "Asphodelaceae",
        "genus": "Aloe",
        "category": "succulent",
        "native_regions": json.dumps(["Arabian Peninsula"]),
        "observation_count": 175,
        "source": "seed",
    },
    {
        "scientific_name": "Acer palmatum",
        "common_names": json.dumps(["Japanese Maple", "Momiji"]),
        "family": "Sapindaceae",
        "genus": "Acer",
        "category": "woody_plant",
        "native_regions": json.dumps(["Japan", "Korea", "China"]),
        "observation_count": 140,
        "source": "seed",
    },
    {
        "scientific_name": "Pothos aureus",
        "common_names": json.dumps(["Devil's Ivy", "Golden Pothos"]),
        "family": "Araceae",
        "genus": "Epipremnum",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Southeast Asia"]),
        "observation_count": 160,
        "source": "seed",
    },
    {
        "scientific_name": "Lavandula angustifolia",
        "common_names": json.dumps(["English Lavender", "Lavender"]),
        "family": "Lamiaceae",
        "genus": "Lavandula",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Mediterranean"]),
        "observation_count": 190,
        "source": "seed",
    },
    {
        "scientific_name": "Cactaceae sp.",
        "common_names": json.dumps(["Cactus"]),
        "family": "Cactaceae",
        "genus": "Cactus",
        "category": "succulent",
        "native_regions": json.dumps(["Americas"]),
        "observation_count": 110,
        "source": "seed",
    },
    {
        "scientific_name": "Mentha spicata",
        "common_names": json.dumps(["Spearmint", "Mint"]),
        "family": "Lamiaceae",
        "genus": "Mentha",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Europe", "Asia"]),
        "observation_count": 170,
        "source": "seed",
    },
    {
        "scientific_name": "Spathiphyllum wallisii",
        "common_names": json.dumps(["Peace Lily", "White Sails"]),
        "family": "Araceae",
        "genus": "Spathiphyllum",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Central America"]),
        "observation_count": 130,
        "source": "seed",
    },
    {
        "scientific_name": "Crassula ovata",
        "common_names": json.dumps(["Jade Plant", "Money Tree"]),
        "family": "Crassulaceae",
        "genus": "Crassula",
        "category": "succulent",
        "native_regions": json.dumps(["South Africa"]),
        "observation_count": 145,
        "source": "seed",
    },
    {
        "scientific_name": "Dracaena marginata",
        "common_names": json.dumps(["Dragon Tree", "Madagascar Dragon Tree"]),
        "family": "Asparagaceae",
        "genus": "Dracaena",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Madagascar"]),
        "observation_count": 105,
        "source": "seed",
    },
    {
        "scientific_name": "Phalaenopsis amabilis",
        "common_names": json.dumps(["Moth Orchid", "Orchid"]),
        "family": "Orchidaceae",
        "genus": "Phalaenopsis",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["Southeast Asia"]),
        "observation_count": 155,
        "source": "seed",
    },
    {
        "scientific_name": "Sansevieria trifasciata",
        "common_names": json.dumps(["Snake Plant", "Mother-in-Law's Tongue"]),
        "family": "Asparagaceae",
        "genus": "Dracaena",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["West Africa"]),
        "observation_count": 165,
        "source": "seed",
    },
    {
        "scientific_name": "Zamioculcas zamiifolia",
        "common_names": json.dumps(["ZZ Plant", "Zanzibar Gem"]),
        "family": "Araceae",
        "genus": "Zamioculcas",
        "category": "herbaceous_flowering_plant",
        "native_regions": json.dumps(["East Africa"]),
        "observation_count": 100,
        "source": "seed",
    },
]


def seed_database() -> dict:
    """Seed the local database with common species.

    Returns dict with seed stats.
    """
    init_db()

    conn = get_connection()
    try:
        existing = conn.execute("SELECT COUNT(*) as cnt FROM species").fetchone()["cnt"]
        if existing > 0:
            logger.info("Database already has %d species, skipping seed", existing)
            return {
                "status": "skipped",
                "reason": f"Database already has {existing} species",
                "species_count": existing,
            }
    finally:
        conn.close()

    count = 0
    for species in SEED_SPECIES:
        insert_species(species)
        count += 1

    logger.info("Seeded %d species into local database", count)
    return {
        "status": "completed",
        "species_count": count,
        "source": "seed",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = seed_database()
    print(json.dumps(result, indent=2))
