import logging

logger = logging.getLogger(__name__)

# Plant care database — species-keyed care instructions
# In production, this would come from a plant database API or cached Supabase data.
# For now, we use common care profiles based on genus/family.

CARE_PROFILES: dict[str, dict] = {
    "default": {
        "watering": {
            "frequency": "When top inch of soil is dry",
            "amount": "Until water drains from bottom",
            "method": "Water soil directly, avoid leaves",
            "seasonal_notes": "Reduce in winter, increase in summer",
        },
        "sunlight": {
            "preference": "Bright indirect light",
            "hours_per_day": "6-8 hours",
            "notes": "Tolerates some direct morning sun",
        },
        "soil": {
            "type": "Well-draining potting mix",
            "ph": "6.0-7.0",
            "drainage": "Essential — no standing water",
            "notes": "Add perlite for extra drainage",
        },
        "temperature": {
            "min_fahrenheit": 50,
            "max_fahrenheit": 95,
            "frost_tender": True,
            "notes": "Keep away from cold drafts",
        },
        "growth": {
            "mature_height": "Varies by species",
            "spread": "Varies by species",
            "growth_rate": "Moderate",
            "bloom_season": "Spring to Summer",
            "bloom_color": "Varies",
        },
        "propagation": {
            "methods": ["Stem cuttings", "Seeds"],
            "difficulty": "Easy",
            "notes": "Root cuttings in water or moist soil",
        },
        "humidity": "40-60% — average household humidity is fine",
        "toxicity": "Check specific species — some are toxic to pets",
        "common_pests": ["Aphids", "Spider mites", "Mealybugs"],
        "general_tips": "Wipe leaves regularly to remove dust",
    },
    "succulent": {
        "watering": {
            "frequency": "Every 2-3 weeks",
            "amount": "Soak thoroughly, then let dry completely",
            "method": "Bottom watering preferred",
            "seasonal_notes": "Water even less in winter (monthly)",
        },
        "sunlight": {
            "preference": "Direct sunlight",
            "hours_per_day": "6+ hours",
            "notes": "Gradually acclimate to prevent sunburn",
        },
        "soil": {
            "type": "Cactus/succulent mix",
            "ph": "5.5-6.5",
            "drainage": "Fast draining — add sand/perlite",
            "notes": "Never use regular potting soil alone",
        },
        "temperature": {
            "min_fahrenheit": 40,
            "max_fahrenheit": 100,
            "frost_tender": True,
            "notes": "Most can't survive frost",
        },
        "growth": {
            "mature_height": "2-12 inches typical",
            "spread": "Varies widely",
            "growth_rate": "Slow",
            "bloom_season": "Varies",
            "bloom_color": "Pink, yellow, white, orange",
        },
        "propagation": {
            "methods": ["Leaf cuttings", "Stem cuttings", "Offsets"],
            "difficulty": "Easy",
            "notes": "Let cuttings callus before planting",
        },
        "humidity": "10-30% — prefers dry air",
        "toxicity": "Most are non-toxic to pets",
        "common_pests": ["Mealybugs", "Scale", "Fungus gnats"],
        "general_tips": "Rotate regularly for even growth",
    },
    "tropical": {
        "watering": {
            "frequency": "Weekly",
            "amount": "Keep soil consistently moist",
            "method": "Water when top inch is dry",
            "seasonal_notes": "Reduce slightly in winter",
        },
        "sunlight": {
            "preference": "Bright indirect to medium light",
            "hours_per_day": "6-10 hours",
            "notes": "Avoid direct afternoon sun",
        },
        "soil": {
            "type": "Rich, well-draining mix",
            "ph": "5.5-7.0",
            "drainage": "Good drainage required",
            "notes": "Add peat moss or coco coir",
        },
        "temperature": {
            "min_fahrenheit": 60,
            "max_fahrenheit": 85,
            "frost_tender": True,
            "notes": "Keep above 60°F at all times",
        },
        "growth": {
            "mature_height": "1-6 feet indoor",
            "spread": "2-4 feet",
            "growth_rate": "Fast in growing season",
            "bloom_season": "Year-round (varies)",
            "bloom_color": "Bright, varied colors",
        },
        "propagation": {
            "methods": ["Stem cuttings", "Air layering", "Division"],
            "difficulty": "Easy to Moderate",
            "notes": "High humidity helps rooting",
        },
        "humidity": "60-80% — mist regularly or use humidifier",
        "toxicity": "Varies — check specific species",
        "common_pests": ["Spider mites", "Thrips", "Scale", "Fungus gnats"],
        "general_tips": "Clean leaves monthly to prevent dust buildup",
    },
    "herb": {
        "watering": {
            "frequency": "When soil surface feels dry",
            "amount": "Moderate — avoid overwatering",
            "method": "Water at base, avoid wetting leaves",
            "seasonal_notes": "More frequent in summer heat",
        },
        "sunlight": {
            "preference": "Full sun to partial shade",
            "hours_per_day": "6-8 hours",
            "notes": "South-facing window ideal",
        },
        "soil": {
            "type": "Light, well-draining",
            "ph": "6.0-7.5",
            "drainage": "Good drainage essential",
            "notes": "Add compost for nutrients",
        },
        "temperature": {
            "min_fahrenheit": 55,
            "max_fahrenheit": 80,
            "frost_tender": True,
            "notes": "Most herbs prefer moderate temps",
        },
        "growth": {
            "mature_height": "6-24 inches",
            "spread": "12-18 inches",
            "growth_rate": "Fast",
            "bloom_season": "Summer (pinch flowers for leaf production)",
            "bloom_color": "Purple, white, blue",
        },
        "propagation": {
            "methods": ["Seeds", "Stem cuttings", "Division"],
            "difficulty": "Easy",
            "notes": "Harvest regularly to encourage bushiness",
        },
        "humidity": "40-60% — average is fine",
        "toxicity": "Most culinary herbs are safe",
        "common_pests": ["Aphids", "Whiteflies", "Spider mites"],
        "general_tips": "Harvest in morning after dew dries for best flavor",
    },
    "tree": {
        "watering": {
            "frequency": "Deep watering weekly",
            "amount": "1-2 inches per week",
            "method": "Water at drip line, not trunk",
            "seasonal_notes": "Increase in drought, reduce in dormancy",
        },
        "sunlight": {
            "preference": "Full sun",
            "hours_per_day": "8+ hours",
            "notes": "Most trees need substantial light",
        },
        "soil": {
            "type": "Deep, well-draining",
            "ph": "6.0-7.5",
            "drainage": "Critical for root health",
            "notes": "Mulch around base (not touching trunk)",
        },
        "temperature": {
            "min_fahrenheit": -40,
            "max_fahrenheit": 100,
            "frost_tender": False,
            "notes": "Depends heavily on species",
        },
        "growth": {
            "mature_height": "15-100+ feet",
            "spread": "15-80 feet",
            "growth_rate": "Slow to moderate",
            "bloom_season": "Spring (varies)",
            "bloom_color": "Varies by species",
        },
        "propagation": {
            "methods": ["Seeds", "Grafting", "Cuttings"],
            "difficulty": "Moderate to Hard",
            "notes": "Some species take years to establish",
        },
        "humidity": "Outdoor ambient — adapts to local climate",
        "toxicity": "Some berries/seeds are toxic — research specific species",
        "common_pests": ["Borers", "Aphids", "Scale", "Gypsy moth"],
        "general_tips": "Proper planting depth is critical — root flare at surface",
    },
}


def get_care_profile(scientific_name: str, genus: str = "", family: str = "") -> dict:
    """Get care instructions for a plant based on its taxonomy.

    Looks up by genus first, then family, then falls back to default profile.

    Args:
        scientific_name: Full scientific name.
        genus: Genus name.
        family: Family name.

    Returns:
        Care profile dict with watering, sunlight, soil, etc.
    """
    name_lower = (scientific_name or "").lower()
    genus_lower = (genus or "").lower()
    family_lower = (family or "").lower()

    # Succulents
    succulent_genera = {"echeveria", "sedum", "crassula", "aloe", "haworthia", "kalanchoe", " sempervivum"}
    succulent_families = {"crassulaceae", "asphodelaceae"}
    if genus_lower in succulent_genera or family_lower in succulent_families:
        return CARE_PROFILES["succulent"]

    # Tropicals
    tropical_genera = {"monstera", "philodendron", "pothos", "dracaena", "palm", "fern"}
    tropical_families = {"araceae", "arecaceae", "polypodiaceae"}
    if genus_lower in tropical_genera or family_lower in tropical_families:
        return CARE_PROFILES["tropical"]

    # Herbs
    herb_genera = {"ocimum", "mentha", "rosmarinum", "thymus", "petroselinum", "coriandrum"}
    if genus_lower in herb_genera or "herb" in name_lower:
        return CARE_PROFILES["herb"]

    # Trees
    tree_genera = {"quercus", "acer", "pinus", "betula", "prunus", "malus"}
    if genus_lower in tree_genera or "tree" in name_lower:
        return CARE_PROFILES["tree"]

    return CARE_PROFILES["default"]
