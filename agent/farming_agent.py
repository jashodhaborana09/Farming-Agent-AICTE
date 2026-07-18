"""
Farming Agent — Main Orchestration Layer
Classifies farmer queries, invokes the right tools, and returns grounded answers.
"""
import asyncio
import logging
import re
from typing import Optional
from tools.weather_service  import get_weather
from tools.market_service   import get_market_prices
from tools.crop_service     import recommend_crops, current_season
from tools.language_service import detect_language, translate_to_english, translate_from_english
from rag.rag_pipeline       import rag_pipeline

logger = logging.getLogger(__name__)

# ── Intent patterns ───────────────────────────────────────────────────────────
WEATHER_PATTERNS  = re.compile(
    r"\b(weather|rain|forecast|temperature|barish|mausam|baarish|varsha|mazha|"
    r"vaadai|vaanam|baarish|pausa|paus|climate|humidity)\b", re.IGNORECASE
)
MARKET_PATTERNS   = re.compile(
    r"\b(price|rate|mandi|market|bhav|dam|bhaav|mol|narakh|kimat|narx|sell|"
    r"tomato|onion|wheat|rice|cotton|soybean|groundnut|maize|potato|"
    r"tur|arhar|moong|urad|mustard|barley|bajra)\b", re.IGNORECASE
)
CROP_PATTERNS     = re.compile(
    r"\b(crop|fasal|phsal|cultivation|grow|plant|sow|seed|kharif|rabi|zaid|"
    r"soil|mitti|recommend|suggest|which crop|best crop)\b", re.IGNORECASE
)
PEST_PATTERNS     = re.compile(
    r"\b(pest|disease|insect|fungus|blight|rust|worm|caterpillar|"
    r"keed|rog|bimari|spray|pesticide|fungicide|neem)\b", re.IGNORECASE
)


def classify_intent(text: str) -> str:
    """Classify the primary intent of a farmer query."""
    if WEATHER_PATTERNS.search(text):
        return "weather"
    if MARKET_PATTERNS.search(text):
        return "market"
    if CROP_PATTERNS.search(text):
        return "crop_advice"
    if PEST_PATTERNS.search(text):
        return "pest_control"
    return "general_farming"


def _extract_city(text: str) -> Optional[str]:
    """Simple city extractor for weather queries."""
    CITY_LIST = [
        "delhi", "mumbai", "bangalore", "hyderabad", "chennai", "kolkata",
        "pune", "ahmedabad", "jaipur", "lucknow", "bhopal", "patna",
        "chandigarh", "amritsar", "nagpur", "surat", "kochi",
        "visakhapatnam", "indore", "coimbatore",
    ]
    text_lower = text.lower()
    for city in CITY_LIST:
        if city in text_lower:
            return city
    return None


def _extract_commodity(text: str) -> Optional[str]:
    """Extract commodity name from market price queries."""
    COMMODITIES = [
        "wheat", "rice", "paddy", "maize", "soybean", "groundnut", "cotton",
        "mustard", "bajra", "jowar", "chickpea", "arhar", "tur", "moong",
        "urad", "lentil", "barley", "sugarcane", "tomato", "onion", "potato",
        "sunflower",
    ]
    text_lower = text.lower()
    for commodity in COMMODITIES:
        if commodity in text_lower:
            return commodity
    return None


def _extract_soil(text: str) -> Optional[str]:
    """Extract soil type from crop queries."""
    SOILS = ["alluvial", "black", "red", "laterite", "sandy", "loamy"]
    text_lower = text.lower()
    for soil in SOILS:
        if soil in text_lower:
            return soil
    return None


class FarmingAgent:
    """
    KrishiMitra — Smart Farming AI Agent
    Orchestrates RAG + tool calls for farmer queries.
    """

    async def chat(
        self,
        user_message: str,
        language: Optional[str] = None,
        city: Optional[str] = None,
        soil_type: Optional[str] = None,
    ) -> dict:
        """
        Process a farmer's message end-to-end:
        1. Detect language
        2. Translate to English for processing
        3. Classify intent
        4. Fetch real-time data (weather / market) if needed
        5. RAG retrieval + IBM Granite generation
        6. Translate answer back to farmer's language
        """
        # 1 — Language detection
        detected_lang = language or detect_language(user_message)
        logger.info("Detected language: %s", detected_lang)

        # 2 — Translate query to English for RAG
        english_query = translate_to_english(user_message, detected_lang)
        logger.info("English query: %s", english_query)

        # 3 — Classify intent
        intent = classify_intent(english_query)
        logger.info("Intent: %s", intent)

        # 4 — Fetch real-time context based on intent
        extra_context = ""
        tool_data     = {}

        if intent == "weather":
            detected_city = city or _extract_city(english_query)
            weather_data  = await get_weather(city=detected_city)
            tool_data["weather"] = weather_data
            if "forecast" in weather_data:
                fc = weather_data["forecast"][:3]
                lines = [
                    f"  {d['date']}: {d['condition']}, Max {d['temp_max_c']}°C, "
                    f"Rain {d['rainfall_mm']}mm"
                    for d in fc
                ]
                extra_context = (
                    f"LIVE WEATHER DATA for {detected_city or 'your location'}:\n"
                    + "\n".join(lines)
                    + f"\nFarming Advisory: {weather_data.get('advisory', '')}"
                )

        elif intent == "market":
            commodity = _extract_commodity(english_query) or "wheat"
            market_data = await get_market_prices(commodity=commodity)
            tool_data["market"] = market_data
            extra_context = (
                f"LIVE MARKET DATA for {market_data.get('commodity', commodity)}:\n"
                f"Modal Price: ₹{market_data.get('modal_price') or market_data.get('msp', 'N/A')}/quintal\n"
                f"Source: {market_data.get('source', '')}\n"
                f"Advice: {market_data.get('advice', '')}"
            )

        elif intent == "crop_advice":
            soil    = soil_type or _extract_soil(english_query) or "loamy"
            season  = current_season()
            crop_data = recommend_crops(soil_type=soil, season=season)
            tool_data["crops"] = crop_data
            top_crops = ", ".join(c["crop"] for c in crop_data["recommended_crops"][:4])
            extra_context = (
                f"CROP RECOMMENDATION ({season.title()} season, {soil.title()} soil):\n"
                f"Recommended crops: {top_crops}\n"
                f"Advisory: {crop_data.get('advisory', '')}\n"
                f"Relevant Schemes: {', '.join(crop_data.get('schemes', []))}"
            )

        # 5 — RAG + IBM Granite generation
        rag_result = rag_pipeline.answer(
            question=english_query,
            language=detected_lang,
            extra_context=extra_context or None,
        )
        english_answer = rag_result["answer"]

        # 6 — Translate answer back to farmer's language
        final_answer = translate_from_english(english_answer, detected_lang)

        return {
            "answer":        final_answer,
            "original_lang": detected_lang,
            "intent":        intent,
            "tool_data":     tool_data,
            "sources":       rag_result.get("sources", []),
            "english_query": english_query,
        }


# module-level singleton
farming_agent = FarmingAgent()
