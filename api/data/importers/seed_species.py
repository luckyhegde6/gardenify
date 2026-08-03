"""Seed the Supabase database with common plant species for testing.

Creates a starter dataset so the API works without downloading
large external datasets. Can be extended with real data later.
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.data.importers.seed_supabase_gbif import seed_supabase_gbif_from_list

logger = logging.getLogger(__name__)

# Common species with basic taxonomy — enough for testing
SEED_SPECIES = [
    {
        "scientific_name": "Monstera deliciosa",
        "common_names": ["Swiss Cheese Plant", "Split-leaf Philodendron"],
        "family": "Araceae",
        "genus": "Monstera",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Central America"],
        "observation_count": 150,
        "source": "seed",
    },
    {
        "scientific_name": "Ficus benjamina",
        "common_names": ["Weeping Fig", "Ficus Tree"],
        "family": "Moraceae",
        "genus": "Ficus",
        "category": "woody_plant",
        "native_regions": ["Southeast Asia"],
        "observation_count": 120,
        "source": "seed",
    },
    {
        "scientific_name": "Echeveria elegans",
        "common_names": ["Mexican Snowball", "Echeveria"],
        "family": "Crassulaceae",
        "genus": "Echeveria",
        "category": "succulent",
        "native_regions": ["Mexico"],
        "observation_count": 95,
        "source": "seed",
    },
    {
        "scientific_name": "Ocimum basilicum",
        "common_names": ["Sweet Basil", "Basil"],
        "family": "Lamiaceae",
        "genus": "Ocimum",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["India", "Southeast Asia"],
        "observation_count": 200,
        "source": "seed",
    },
    {
        "scientific_name": "Rosa damascena",
        "common_names": ["Damask Rose", "Rose"],
        "family": "Rosaceae",
        "genus": "Rosa",
        "category": "woody_plant",
        "native_regions": ["Middle East"],
        "observation_count": 180,
        "source": "seed",
    },
    {
        "scientific_name": "Quercus robur",
        "common_names": ["English Oak", "Pedunculate Oak"],
        "family": "Fagaceae",
        "genus": "Quercus",
        "category": "woody_plant",
        "native_regions": ["Europe"],
        "observation_count": 300,
        "source": "seed",
    },
    {
        "scientific_name": "Helianthus annuus",
        "common_names": ["Common Sunflower", "Sunflower"],
        "family": "Asteraceae",
        "genus": "Helianthus",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["North America"],
        "observation_count": 250,
        "source": "seed",
    },
    {
        "scientific_name": "Nephrolepis exaltata",
        "common_names": ["Boston Fern", "Sword Fern"],
        "family": "Nephrolepidaceae",
        "genus": "Nephrolepis",
        "category": "fern",
        "native_regions": ["Tropics"],
        "observation_count": 85,
        "source": "seed",
    },
    {
        "scientific_name": "Aloe vera",
        "common_names": ["Aloe Vera", "Burn Plant"],
        "family": "Asphodelaceae",
        "genus": "Aloe",
        "category": "succulent",
        "native_regions": ["Arabian Peninsula"],
        "observation_count": 175,
        "source": "seed",
    },
    {
        "scientific_name": "Acer palmatum",
        "common_names": ["Japanese Maple", "Momiji"],
        "family": "Sapindaceae",
        "genus": "Acer",
        "category": "woody_plant",
        "native_regions": ["Japan", "Korea", "China"],
        "observation_count": 140,
        "source": "seed",
    },
    {
        "scientific_name": "Pothos aureus",
        "common_names": ["Devil's Ivy", "Golden Pothos"],
        "family": "Araceae",
        "genus": "Epipremnum",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Southeast Asia"],
        "observation_count": 160,
        "source": "seed",
    },
    {
        "scientific_name": "Lavandula angustifolia",
        "common_names": ["English Lavender", "Lavender"],
        "family": "Lamiaceae",
        "genus": "Lavandula",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Mediterranean"],
        "observation_count": 190,
        "source": "seed",
    },
    {
        "scientific_name": "Cactaceae sp.",
        "common_names": ["Cactus"],
        "family": "Cactaceae",
        "genus": "Cactus",
        "category": "succulent",
        "native_regions": ["Americas"],
        "observation_count": 110,
        "source": "seed",
    },
    {
        "scientific_name": "Mentha spicata",
        "common_names": ["Spearmint", "Mint"],
        "family": "Lamiaceae",
        "genus": "Mentha",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Europe", "Asia"],
        "observation_count": 170,
        "source": "seed",
    },
    {
        "scientific_name": "Spathiphyllum wallisii",
        "common_names": ["Peace Lily", "White Sails"],
        "family": "Araceae",
        "genus": "Spathiphyllum",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Central America"],
        "observation_count": 130,
        "source": "seed",
    },
    {
        "scientific_name": "Crassula ovata",
        "common_names": ["Jade Plant", "Money Tree"],
        "family": "Crassulaceae",
        "genus": "Crassula",
        "category": "succulent",
        "native_regions": ["South Africa"],
        "observation_count": 145,
        "source": "seed",
    },
    {
        "scientific_name": "Dracaena marginata",
        "common_names": ["Dragon Tree", "Madagascar Dragon Tree"],
        "family": "Asparagaceae",
        "genus": "Dracaena",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Madagascar"],
        "observation_count": 105,
        "source": "seed",
    },
    {
        "scientific_name": "Phalaenopsis amabilis",
        "common_names": ["Moth Orchid", "Orchid"],
        "family": "Orchidaceae",
        "genus": "Phalaenopsis",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["Southeast Asia"],
        "observation_count": 155,
        "source": "seed",
    },
    {
        "scientific_name": "Sansevieria trifasciata",
        "common_names": ["Snake Plant", "Mother-in-Law's Tongue"],
        "family": "Asparagaceae",
        "genus": "Dracaena",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["West Africa"],
        "observation_count": 165,
        "source": "seed",
    },
    {
        "scientific_name": "Zamioculcas zamiifolia",
        "common_names": ["ZZ Plant", "Zanzibar Gem"],
        "family": "Araceae",
        "genus": "Zamioculcas",
        "category": "herbaceous_flowering_plant",
        "native_regions": ["East Africa"],
        "observation_count": 100,
        "source": "seed",
    },
]


def seed_database() -> dict:
    """Seed the Supabase database with common species.

    Returns dict with seed stats.
    """
    stats = seed_supabase_gbif_from_list(SEED_SPECIES)

    logger.info("Seeded %d species into Supabase", len(SEED_SPECIES))
    return {
        "status": "completed",
        "species_count": len(SEED_SPECIES),
        "source": "seed",
        **stats,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = seed_database()
    print(json.dumps(result, indent=2))
