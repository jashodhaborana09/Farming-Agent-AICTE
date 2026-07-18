"""
Crop Recommendation Engine
Returns season-appropriate, soil-matched crop suggestions.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Current Indian farming season based on month
def current_season() -> str:
    month = datetime.now().month
    if 6 <= month <= 9:
        return "kharif"
    elif 10 <= month <= 2 or month == 1:
        return "rabi"
    else:
        return "zaid"


CROP_DB = {
    "kharif": {
        "alluvial":  ["Rice", "Maize", "Sugarcane", "Moong", "Urad"],
        "black":     ["Cotton", "Jowar", "Soybean", "Groundnut"],
        "red":       ["Groundnut", "Rice", "Maize", "Bajra"],
        "laterite":  ["Cashew", "Tapioca", "Rice"],
        "sandy":     ["Bajra", "Guar", "Groundnut", "Watermelon"],
        "loamy":     ["Maize", "Soybean", "Groundnut", "Rice"],
        "default":   ["Rice", "Maize", "Bajra", "Soybean", "Cotton"],
    },
    "rabi": {
        "alluvial":  ["Wheat", "Barley", "Mustard", "Peas"],
        "black":     ["Chickpea", "Linseed", "Safflower"],
        "red":       ["Wheat", "Mustard", "Chickpea"],
        "laterite":  ["Potato", "Mustard", "Peas"],
        "sandy":     ["Mustard", "Barley"],
        "loamy":     ["Wheat", "Mustard", "Chickpea", "Lentil"],
        "default":   ["Wheat", "Mustard", "Chickpea", "Barley"],
    },
    "zaid": {
        "alluvial":  ["Watermelon", "Muskmelon", "Cucumber", "Moong"],
        "black":     ["Bitter Gourd", "Ridge Gourd", "Soybean"],
        "red":       ["Watermelon", "Cucumber", "Moong"],
        "laterite":  ["Cucumber", "Pumpkin"],
        "sandy":     ["Watermelon", "Muskmelon"],
        "loamy":     ["Vegetable crops", "Moong", "Cucumber", "Watermelon"],
        "default":   ["Watermelon", "Cucumber", "Moong", "Urad"],
    },
}

SOIL_DESCRIPTIONS = {
    "alluvial": "Alluvial soil — fertile, found in Indo-Gangetic plains. Suits most crops.",
    "black":    "Black/Regur soil — clay-rich, water-retentive. Best for cotton & sorghum.",
    "red":      "Red & yellow soil — low fertility, needs fertilizers. Good for coarse grains.",
    "laterite": "Laterite soil — leached, acidic. Suited for plantation crops.",
    "sandy":    "Sandy/desert soil — poor water retention. Drought-tolerant crops preferred.",
    "loamy":    "Loamy soil — best all-round soil, ideal for vegetables and cereals.",
}

CROP_DETAILS = {
    "Rice":       {"water": "High", "duration_days": 110, "profit": "Medium", "market": "Strong"},
    "Wheat":      {"water": "Medium", "duration_days": 120, "profit": "Medium", "market": "Strong"},
    "Cotton":     {"water": "Medium", "duration_days": 180, "profit": "High",   "market": "Strong"},
    "Soybean":    {"water": "Medium", "duration_days": 95,  "profit": "Medium", "market": "Good"},
    "Groundnut":  {"water": "Low",    "duration_days": 110, "profit": "High",   "market": "Good"},
    "Maize":      {"water": "Medium", "duration_days": 80,  "profit": "Medium", "market": "Good"},
    "Tomato":     {"water": "High",   "duration_days": 70,  "profit": "High",   "market": "Variable"},
    "Mustard":    {"water": "Low",    "duration_days": 90,  "profit": "Medium", "market": "Good"},
    "Chickpea":   {"water": "Low",    "duration_days": 100, "profit": "Medium", "market": "Strong"},
    "Watermelon": {"water": "Medium", "duration_days": 70,  "profit": "High",   "market": "Seasonal"},
    "Bajra":      {"water": "Low",    "duration_days": 75,  "profit": "Low",    "market": "Moderate"},
}


def recommend_crops(
    soil_type: Optional[str] = None,
    season: Optional[str] = None,
    water_availability: Optional[str] = None,
    location: Optional[str] = None,
    area_acres: Optional[float] = None,
) -> dict:
    """
    Recommend crops based on soil type, season, and water availability.
    Returns ranked crop list with profitability and market guidance.
    """
    detected_season = season or current_season()
    detected_soil   = (soil_type or "default").lower().strip()

    season_crops = CROP_DB.get(detected_season, CROP_DB["kharif"])
    crops = season_crops.get(detected_soil, season_crops["default"])

    # Filter by water availability
    if water_availability and water_availability.lower() == "low":
        low_water = {c for c, d in CROP_DETAILS.items() if d["water"] == "Low"}
        filtered  = [c for c in crops if c in low_water]
        crops     = filtered if filtered else crops

    # Enrich with details
    enriched = []
    for crop in crops[:6]:
        details = CROP_DETAILS.get(crop, {})
        enriched.append({
            "crop":           crop,
            "water_need":     details.get("water", "Medium"),
            "duration_days":  details.get("duration_days", "~90"),
            "profit_level":   details.get("profit", "Medium"),
            "market_demand":  details.get("market", "Good"),
        })

    soil_desc = SOIL_DESCRIPTIONS.get(detected_soil, "")
    advisory  = _crop_advisory(detected_season, detected_soil, water_availability)

    return {
        "season":       detected_season.title(),
        "soil_type":    detected_soil.title(),
        "soil_desc":    soil_desc,
        "recommended_crops": enriched,
        "advisory":     advisory,
        "schemes":      _relevant_schemes(crops),
    }


def _crop_advisory(season: str, soil: str, water: Optional[str]) -> str:
    tips = []
    if season == "kharif":
        tips.append("Sow kharif crops after first monsoon rain (mid-June to July).")
    elif season == "rabi":
        tips.append("Rabi sowing window: October 15 – November 30. Avoid late sowing for wheat.")
    else:
        tips.append("Summer crops need reliable irrigation. Sow in March-April.")

    if water == "low":
        tips.append("With limited water, choose drought-tolerant varieties (Bajra, Pulses, Mustard).")
    elif water == "high":
        tips.append("Good water availability — rice, sugarcane, and vegetables are excellent choices.")

    if soil == "black":
        tips.append("Black soil retains moisture — reduce irrigation frequency.")
    elif soil in ("sandy", "red"):
        tips.append("Apply organic matter/FYM to improve water retention in this soil type.")

    return " | ".join(tips)


def _relevant_schemes(crops: list[str]) -> list[str]:
    schemes = ["PM-KISAN: ₹6000/yr direct support", "Soil Health Card: Free soil testing"]
    if any(c in crops for c in ["Rice", "Wheat", "Cotton"]):
        schemes.append("PM Fasal Bima Yojana: Crop insurance at low premium")
    if any(c in crops for c in ["Tomato", "Watermelon", "Cucumber"]):
        schemes.append("MIDH: Horticulture development subsidy available")
    schemes.append("eNAM: Online mandi for better price discovery")
    return schemes
