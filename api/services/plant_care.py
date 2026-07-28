"""Plant care profiles by taxonomy. Maps genus/family → care instructions."""

import logging

logger = logging.getLogger(__name__)

W = {"frequency": "", "amount": "", "method": "", "seasonal_notes": ""}
S = {"preference": "", "hours_per_day": "", "notes": ""}
SO = {"type": "", "ph": "", "drainage": "", "notes": ""}
T = {"min_fahrenheit": 50, "max_fahrenheit": 95, "frost_tender": True, "notes": ""}
G = {"mature_height": "", "spread": "", "growth_rate": "", "bloom_season": "", "bloom_color": ""}
P = {"methods": [], "difficulty": "", "notes": ""}

_PROFILES = {
    "default": {
        "watering": {
            **W, "frequency": "When top inch dry", "amount": "Until drains",
            "method": "Water soil, not leaves",
        },
        "sunlight": {**S, "preference": "Bright indirect", "hours_per_day": "6-8h"},
        "soil": {**SO, "type": "Well-draining mix", "ph": "6.0-7.0", "drainage": "Essential"},
        "temperature": {**T},
        "growth": {**G, "growth_rate": "Moderate", "bloom_season": "Spring-Summer"},
        "propagation": {**P, "methods": ["Stem cuttings", "Seeds"], "difficulty": "Easy"},
        "humidity": "40-60%", "toxicity": "Check species", "common_pests": ["Aphids", "Spider mites"],
        "general_tips": "Wipe leaves to remove dust",
    },
    "succulent": {
        "watering": {
            **W, "frequency": "Every 2-3 weeks", "amount": "Soak then dry completely",
            "method": "Bottom water",
        },
        "sunlight": {**S, "preference": "Direct sun", "hours_per_day": "6+h"},
        "soil": {**SO, "type": "Cactus mix", "ph": "5.5-6.5", "drainage": "Fast — add sand"},
        "temperature": {**T, "min_fahrenheit": 40},
        "growth": {**G, "mature_height": "2-12in", "growth_rate": "Slow"},
        "propagation": {**P, "methods": ["Leaf cuttings", "Offsets"], "difficulty": "Easy"},
        "humidity": "10-30%", "toxicity": "Non-toxic", "common_pests": ["Mealybugs", "Scale"],
        "general_tips": "Rotate for even growth",
    },
    "tropical": {
        "watering": {**W, "frequency": "Weekly", "amount": "Keep moist", "method": "Top inch dry check"},
        "sunlight": {**S, "preference": "Bright indirect", "hours_per_day": "6-10h"},
        "soil": {**SO, "type": "Rich mix", "ph": "5.5-7.0", "drainage": "Good required"},
        "temperature": {**T, "min_fahrenheit": 60},
        "growth": {**G, "mature_height": "1-6ft", "growth_rate": "Fast"},
        "propagation": {**P, "methods": ["Stem cuttings", "Air layering"], "difficulty": "Easy-Moderate"},
        "humidity": "60-80%", "toxicity": "Varies", "common_pests": ["Spider mites", "Thrips"],
        "general_tips": "Clean leaves monthly",
    },
    "herb": {
        "watering": {**W, "frequency": "When surface dry", "amount": "Moderate", "method": "Water at base"},
        "sunlight": {**S, "preference": "Full sun", "hours_per_day": "6-8h"},
        "soil": {**SO, "type": "Light, draining", "ph": "6.0-7.5", "drainage": "Essential"},
        "temperature": {**T, "min_fahrenheit": 55, "max_fahrenheit": 80},
        "growth": {**G, "mature_height": "6-24in", "growth_rate": "Fast"},
        "propagation": {**P, "methods": ["Seeds", "Cuttings"], "difficulty": "Easy"},
        "humidity": "40-60%", "toxicity": "Safe", "common_pests": ["Aphids", "Whiteflies"],
        "general_tips": "Harvest in morning for best flavor",
    },
    "tree": {
        "watering": {**W, "frequency": "Weekly deep", "amount": "1-2in/week", "method": "At drip line"},
        "sunlight": {**S, "preference": "Full sun", "hours_per_day": "8+h"},
        "soil": {**SO, "type": "Deep, draining", "ph": "6.0-7.5", "drainage": "Critical"},
        "temperature": {**T, "min_fahrenheit": -40, "frost_tender": False},
        "growth": {**G, "mature_height": "15-100+ft", "growth_rate": "Slow"},
        "propagation": {**P, "methods": ["Seeds", "Grafting"], "difficulty": "Moderate-Hard"},
        "humidity": "Ambient", "toxicity": "Research species", "common_pests": ["Borers", "Scale"],
        "general_tips": "Root flare at surface level",
    },
}

# Taxonomy → profile mapping
_GENUS_MAP = {
    "succulent": {"echeveria", "sedum", "crassula", "aloe", "haworthia", "kalanchoe", "sempervivum"},
    "tropical": {"monstera", "philodendron", "pothos", "dracaena", "palm", "fern"},
    "herb": {"ocimum", "mentha", "rosmarinum", "thymus", "petroselinum", "coriandrum"},
    "tree": {"quercus", "acer", "pinus", "betula", "prunus", "malus"},
}
_FAMILY_MAP = {
    "succulent": {"crassulaceae", "asphodelaceae"},
    "tropical": {"araceae", "arecaceae", "polypodiaceae"},
}


def get_care_profile(scientific_name: str = "", genus: str = "", family: str = "") -> dict:
    """Look up care by genus → family → default."""
    g = genus.lower()
    f = family.lower()
    name = scientific_name.lower()

    for profile, genera in _GENUS_MAP.items():
        if g in genera or any(k in name for k in [profile]):
            return _PROFILES[profile]

    for profile, families in _FAMILY_MAP.items():
        if f in families:
            return _PROFILES[profile]

    return _PROFILES["default"]
