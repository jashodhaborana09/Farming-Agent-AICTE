"""
Market Price Service
Fetches live mandi (market) prices from data.gov.in Agmarknet API.
Falls back to curated MSP data when live API is unavailable.
"""
import logging
import aiohttp
from typing import Optional
import config

logger = logging.getLogger(__name__)

# MSP 2024-25 fallback data (₹ per quintal)
MSP_2024 = {
    "wheat":       {"msp": 2275,  "unit": "₹/quintal", "season": "Rabi"},
    "rice":        {"msp": 2300,  "unit": "₹/quintal", "season": "Kharif"},
    "paddy":       {"msp": 2300,  "unit": "₹/quintal", "season": "Kharif"},
    "maize":       {"msp": 2090,  "unit": "₹/quintal", "season": "Kharif"},
    "soybean":     {"msp": 4600,  "unit": "₹/quintal", "season": "Kharif"},
    "groundnut":   {"msp": 6783,  "unit": "₹/quintal", "season": "Kharif"},
    "cotton":      {"msp": 7521,  "unit": "₹/quintal", "season": "Kharif"},
    "mustard":     {"msp": 5950,  "unit": "₹/quintal", "season": "Rabi"},
    "sunflower":   {"msp": 7280,  "unit": "₹/quintal", "season": "Kharif"},
    "bajra":       {"msp": 2625,  "unit": "₹/quintal", "season": "Kharif"},
    "jowar":       {"msp": 3371,  "unit": "₹/quintal", "season": "Kharif"},
    "chickpea":    {"msp": 5440,  "unit": "₹/quintal", "season": "Rabi"},
    "arhar":       {"msp": 7550,  "unit": "₹/quintal", "season": "Kharif"},
    "tur":         {"msp": 7550,  "unit": "₹/quintal", "season": "Kharif"},
    "moong":       {"msp": 8682,  "unit": "₹/quintal", "season": "Kharif"},
    "urad":        {"msp": 7400,  "unit": "₹/quintal", "season": "Kharif"},
    "lentil":      {"msp": 6425,  "unit": "₹/quintal", "season": "Rabi"},
    "barley":      {"msp": 1735,  "unit": "₹/quintal", "season": "Rabi"},
    "sugarcane":   {"msp": 340,   "unit": "₹/quintal (FRP)", "season": "Annual"},
    "tomato":      {"msp": None,  "unit": "₹/quintal", "season": "All"},
    "onion":       {"msp": None,  "unit": "₹/quintal", "season": "All"},
    "potato":      {"msp": None,  "unit": "₹/quintal", "season": "All"},
}

# Simulated live mandi prices (representative ranges for demo)
LIVE_MANDI_PRICES = {
    "tomato":   {"min": 800,  "max": 2400, "modal": 1600, "unit": "₹/quintal"},
    "onion":    {"min": 600,  "max": 2200, "modal": 1400, "unit": "₹/quintal"},
    "potato":   {"min": 500,  "max": 1800, "modal": 1100, "unit": "₹/quintal"},
    "wheat":    {"min": 2200, "max": 2500, "modal": 2350, "unit": "₹/quintal"},
    "rice":     {"min": 2100, "max": 2800, "modal": 2500, "unit": "₹/quintal"},
    "maize":    {"min": 1900, "max": 2300, "modal": 2100, "unit": "₹/quintal"},
    "soybean":  {"min": 4200, "max": 5100, "modal": 4700, "unit": "₹/quintal"},
    "groundnut":{"min": 5500, "max": 7200, "modal": 6400, "unit": "₹/quintal"},
    "cotton":   {"min": 6500, "max": 8200, "modal": 7200, "unit": "₹/quintal"},
    "mustard":  {"min": 5400, "max": 6400, "modal": 5900, "unit": "₹/quintal"},
    "arhar":    {"min": 6800, "max": 8400, "modal": 7400, "unit": "₹/quintal"},
    "moong":    {"min": 7500, "max": 9500, "modal": 8400, "unit": "₹/quintal"},
}


async def get_market_prices(
    commodity: str,
    state:     Optional[str] = None,
    district:  Optional[str] = None,
) -> dict:
    """
    Fetch current mandi price for a commodity.
    Tries live Agmarknet API first, falls back to MSP / simulated data.
    """
    commodity_lower = commodity.lower().strip()

    # Attempt live Agmarknet API
    live_data = await _fetch_agmarknet(commodity_lower, state, district)
    if live_data:
        return live_data

    # Fall back to simulated / MSP data
    return _fallback_price(commodity_lower, state)


async def _fetch_agmarknet(commodity: str, state: Optional[str], district: Optional[str]) -> Optional[dict]:
    """Query data.gov.in Agmarknet API for live prices."""
    if not config.AGMARKET_API_KEY:
        return None

    params = {
        "api-key":  config.AGMARKET_API_KEY,
        "format":   "json",
        "filters[commodity]": commodity.title(),
        "limit":    5,
    }
    if state:
        params["filters[state]"] = state.title()
    if district:
        params["filters[district]"] = district.title()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                config.AGMARKET_BASE_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as resp:
                data = await resp.json()

        records = data.get("records", [])
        if not records:
            return None

        prices = []
        for rec in records:
            try:
                prices.append({
                    "market":    rec.get("Market", ""),
                    "district":  rec.get("District", ""),
                    "state":     rec.get("State", ""),
                    "min_price": float(rec.get("Min Price", 0)),
                    "max_price": float(rec.get("Max Price", 0)),
                    "modal_price":float(rec.get("Modal Price", 0)),
                    "date":      rec.get("Arrival Date", ""),
                })
            except (ValueError, KeyError):
                continue

        if not prices:
            return None

        modal_avg = sum(p["modal_price"] for p in prices) / len(prices)
        return {
            "commodity":   commodity.title(),
            "source":      "Agmarknet (Live)",
            "markets":     prices,
            "avg_modal":   round(modal_avg, 2),
            "unit":        "₹/quintal",
            "advice":      _price_advice(commodity, modal_avg),
        }

    except Exception as exc:
        logger.warning("Agmarknet API error: %s", exc)
        return None


def _fallback_price(commodity: str, state: Optional[str]) -> dict:
    """Return MSP or simulated price data with trading advice."""
    live = LIVE_MANDI_PRICES.get(commodity)
    msp_info = MSP_2024.get(commodity, {})

    if live:
        modal = live["modal"]
        result = {
            "commodity":  commodity.title(),
            "source":     "Reference Market Data",
            "min_price":  live["min"],
            "max_price":  live["max"],
            "modal_price": modal,
            "unit":       live["unit"],
            "msp":        msp_info.get("msp"),
            "season":     msp_info.get("season", ""),
            "advice":     _price_advice(commodity, modal, msp_info.get("msp")),
        }
    elif msp_info:
        result = {
            "commodity":  commodity.title(),
            "source":     "MSP 2024-25 (Government)",
            "msp":        msp_info.get("msp"),
            "unit":       msp_info.get("unit", "₹/quintal"),
            "season":     msp_info.get("season", ""),
            "advice":     (
                f"MSP for {commodity.title()} is ₹{msp_info.get('msp')}/quintal. "
                "Ensure you sell through APMC or eNAM to get at least MSP."
            ),
        }
    else:
        result = {
            "commodity": commodity.title(),
            "source":    "Not found",
            "advice":    (
                f"Price data not available for '{commodity.title()}'. "
                "Check agmarknet.gov.in or your local APMC mandi."
            ),
        }

    return result


def _price_advice(commodity: str, modal_price: float, msp: Optional[float] = None) -> str:
    """Generate selling advice based on current price vs MSP."""
    tips = []

    if msp and modal_price < msp:
        tips.append(
            f"⚠️ Current price (₹{modal_price:.0f}/qtl) is BELOW MSP (₹{msp}/qtl). "
            "Sell through government procurement centres (APMC/FCI) to get MSP."
        )
    elif msp and modal_price >= msp:
        tips.append(
            f"✅ Current price (₹{modal_price:.0f}/qtl) is above MSP (₹{msp}/qtl). "
            "Good time to sell in open market."
        )

    # Crop-specific advice
    if commodity in ("tomato", "onion", "potato"):
        tips.append(
            "Vegetable prices fluctuate widely. Use cold storage if price is low; "
            "sell when price rises above ₹1500/quintal for better margins."
        )
    if commodity in ("wheat", "rice", "paddy"):
        tips.append("Register on eNAM (enam.gov.in) for transparent price discovery across mandis.")

    return " ".join(tips) if tips else f"Current modal price: ₹{modal_price:.0f}/quintal."
