"""
Smoke test — verify IBM watsonx.ai credentials are working.
"""
import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def test_granite_llm():
    logger.info("Testing IBM Granite LLM…")
    from rag.granite_client import GraniteClient
    client = GraniteClient()
    response = client.generate("What is the best crop for black soil in summer?")
    logger.info("LLM response: %s", response[:200])
    assert len(response) > 0, "Empty response from Granite LLM"
    logger.info("✅ Granite LLM test passed.")


def test_granite_embed():
    logger.info("Testing IBM Granite Embeddings…")
    from rag.granite_client import GraniteClient
    client = GraniteClient()
    embeddings = client.embed(["test farming query"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) > 0
    logger.info("✅ Granite Embeddings test passed (dim=%d).", len(embeddings[0]))


def test_weather():
    logger.info("Testing Weather Service…")
    result = asyncio.run(__import__("tools.weather_service", fromlist=["get_weather"]).get_weather(city="delhi"))
    assert "forecast" in result or "error" in result
    logger.info("✅ Weather service test passed.")
    if "forecast" in result:
        logger.info("  Today: %s", result["forecast"][0])


def test_market():
    logger.info("Testing Market Service…")
    result = asyncio.run(__import__("tools.market_service", fromlist=["get_market_prices"]).get_market_prices("wheat"))
    assert "commodity" in result
    logger.info("✅ Market service test passed: %s", result)


def test_crop():
    logger.info("Testing Crop Recommendation…")
    from tools.crop_service import recommend_crops
    result = recommend_crops(soil_type="alluvial", season="kharif")
    assert len(result["recommended_crops"]) > 0
    logger.info("✅ Crop service test passed: %s", [c["crop"] for c in result["recommended_crops"]])


def test_language():
    logger.info("Testing Language Service…")
    from tools.language_service import detect_language, translate_to_english
    lang = detect_language("धान की फसल के लिए खाद कब डालें?")
    logger.info("  Detected language: %s", lang)
    english = translate_to_english("धान की फसल के लिए खाद कब डालें?", "hi")
    logger.info("  Translated: %s", english)
    logger.info("✅ Language service test passed.")


if __name__ == "__main__":
    tests = [
        ("Weather",    test_weather),
        ("Market",     test_market),
        ("Crop",       test_crop),
        ("Language",   test_language),
    ]

    # IBM credential-dependent tests only if flag passed
    if "--with-ibm" in sys.argv:
        tests = [("Granite LLM", test_granite_llm), ("Granite Embed", test_granite_embed)] + tests

    passed = failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as exc:
            logger.error("❌ %s test FAILED: %s", name, exc)
            failed += 1

    logger.info("\n=== Results: %d passed, %d failed ===", passed, failed)
    sys.exit(0 if failed == 0 else 1)
