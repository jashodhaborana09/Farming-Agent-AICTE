"""
Weather Service — fetches real-time forecasts via Open-Meteo (free, no API key)
"""
import logging
import aiohttp
from datetime import datetime
from typing import Optional
import config

logger = logging.getLogger(__name__)

# WMO weather interpretation codes
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}

# Major Indian city coordinates for quick lookup
CITY_COORDS = {
    "delhi":     (28.6139, 77.2090), "mumbai":     (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946), "hyderabad":  (17.3850, 78.4867),
    "chennai":   (13.0827, 80.2707), "kolkata":    (22.5726, 88.3639),
    "pune":      (18.5204, 73.8567), "ahmedabad":  (23.0225, 72.5714),
    "jaipur":    (26.9124, 75.7873), "lucknow":    (26.8467, 80.9462),
    "bhopal":    (23.2599, 77.4126), "patna":      (25.5941, 85.1376),
    "chandigarh":(30.7333, 76.7794), "amritsar":   (31.6340, 74.8723),
    "nagpur":    (21.1458, 79.0882), "surat":      (21.1702, 72.8311),
    "kochi":     (9.9312,  76.2673), "visakhapatnam": (17.6868, 83.2185),
    "indore":    (22.7196, 75.8577), "coimbatore": (11.0168, 76.9558),
}


async def get_weather(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> dict:
    """
    Fetch 3-day weather forecast for a city or lat/lon.
    Returns structured forecast suitable for farming decisions.
    """
    if city:
        city_lower = city.lower().strip()
        coords = CITY_COORDS.get(city_lower)
        if coords:
            lat, lon = coords
        else:
            # Default to a central India location if city not found
            lat, lon = 20.5937, 78.9629

    if lat is None or lon is None:
        lat, lon = 20.5937, 78.9629  # centre of India

    url = (
        f"{config.OPEN_METEO_BASE_URL}/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"weathercode,windspeed_10m_max,et0_fao_evapotranspiration"
        f"&current_weather=true"
        f"&timezone=Asia%2FKolkata"
        f"&forecast_days=7"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()

        current = data.get("current_weather", {})
        daily   = data.get("daily", {})
        dates   = daily.get("time", [])

        forecast_days = []
        for i in range(min(7, len(dates))):
            wmo = daily.get("weathercode", [])[i] if daily.get("weathercode") else 0
            forecast_days.append({
                "date":           dates[i],
                "condition":      WMO_CODES.get(wmo, "Unknown"),
                "temp_max_c":     daily.get("temperature_2m_max", [])[i],
                "temp_min_c":     daily.get("temperature_2m_min", [])[i],
                "rainfall_mm":    daily.get("precipitation_sum", [])[i],
                "wind_kmh":       daily.get("windspeed_10m_max", [])[i],
                "evapotrans_mm":  daily.get("et0_fao_evapotranspiration", [])[i],
            })

        # Farming advisory from weather
        advisory = _weather_advisory(forecast_days)

        return {
            "location":  {"lat": lat, "lon": lon, "city": city or ""},
            "current":   {
                "temp_c":    current.get("temperature"),
                "wind_kmh":  current.get("windspeed"),
                "condition": WMO_CODES.get(current.get("weathercode", 0), "Clear"),
            },
            "forecast":  forecast_days,
            "advisory":  advisory,
        }

    except Exception as exc:
        logger.error("Weather fetch failed: %s", exc)
        return {"error": str(exc), "advisory": "Could not fetch weather data."}


def _weather_advisory(forecast: list[dict]) -> str:
    """Generate a short farming advisory from weather forecast."""
    if not forecast:
        return "No forecast data available."

    today = forecast[0]
    rain  = today.get("rainfall_mm", 0) or 0
    tmax  = today.get("temp_max_c",  35) or 35
    wind  = today.get("wind_kmh",     0) or 0

    tips = []
    if rain > 20:
        tips.append("Heavy rain expected — avoid spraying pesticides today. Ensure field drainage.")
    elif rain > 5:
        tips.append("Light rain expected — good for sowing and transplanting activities.")
    else:
        tips.append("Dry conditions — ensure adequate irrigation for crops.")

    if tmax > 40:
        tips.append("Extreme heat — irrigate in the early morning or evening to reduce evaporation.")
    elif tmax < 12:
        tips.append("Cold conditions — protect young seedlings from frost; delay sowing if possible.")

    if wind > 50:
        tips.append("High winds expected — avoid spraying operations; support tall crops.")

    total_rain = sum(d.get("rainfall_mm", 0) or 0 for d in forecast[:7])
    if total_rain > 100:
        tips.append(f"Week total rainfall: {total_rain:.0f}mm — watch for waterlogging and fungal diseases.")
    elif total_rain < 10:
        tips.append(f"Dry week ahead ({total_rain:.0f}mm) — plan irrigation schedule carefully.")

    return " | ".join(tips)
