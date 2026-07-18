"""
Language Detection and Translation Service
Detects farmer input language and translates for internal processing.
"""
import logging
from typing import Optional
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import config

# Deterministic language detection
DetectorFactory.seed = 42
logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """Detect ISO language code of input text. Returns 'en' on failure."""
    try:
        lang = detect(text)
        return lang if lang in config.SUPPORTED_LANGUAGES else "en"
    except Exception:
        return "en"


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate text to English for RAG processing."""
    if source_lang == "en":
        return text
    try:
        translated = GoogleTranslator(source=source_lang, target="en").translate(text)
        return translated or text
    except Exception as exc:
        logger.warning("Translation to English failed: %s", exc)
        return text


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English answer back to farmer's language."""
    if target_lang == "en":
        return text
    try:
        translated = GoogleTranslator(source="en", target=target_lang).translate(text)
        return translated or text
    except Exception as exc:
        logger.warning("Translation from English failed: %s", exc)
        return text  # Return English if translation fails


def get_language_name(lang_code: str) -> str:
    """Get human-readable language name from code."""
    return config.SUPPORTED_LANGUAGES.get(lang_code, "English")


# Language-specific greeting messages
GREETINGS = {
    "en": "Hello! I am KrishiMitra, your smart farming assistant. How can I help you today?",
    "hi": "नमस्ते! मैं कृषिमित्र हूं, आपका स्मार्ट कृषि सहायक। आज मैं आपकी कैसे मदद कर सकता हूं?",
    "ta": "வணக்கம்! நான் கிருஷிமித்ரா, உங்கள் ஸ்மார்ட் விவசாய உதவியாளர். நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?",
    "te": "నమస్కారం! నేను కృషిమిత్ర, మీ స్మార్ట్ వ్యవసాయ సహాయకుడు. నేను మీకు ఎలా సహాయం చేయగలను?",
    "kn": "ನಮಸ್ಕಾರ! ನಾನು ಕೃಷಿಮಿತ್ರ, ನಿಮ್ಮ ಸ್ಮಾರ್ಟ್ ಕೃಷಿ ಸಹಾಯಕ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    "mr": "नमस्कार! मी कृषिमित्र आहे, तुमचा स्मार्ट शेती सहाय्यक. मी तुम्हाला कशी मदत करू शकतो?",
    "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕ੍ਰਿਸ਼ੀਮਿੱਤਰ ਹਾਂ, ਤੁਹਾਡਾ ਸਮਾਰਟ ਖੇਤੀ ਸਹਾਇਕ। ਮੈਂ ਅੱਜ ਤੁਹਾਡੀ ਕਿਵੇਂ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ?",
    "bn": "নমস্কার! আমি কৃষিমিত্র, আপনার স্মার্ট কৃষি সহায়ক। আজ আমি আপনাকে কীভাবে সাহায্য করতে পারি?",
    "gu": "નમસ્તે! હું કૃષિમિત્ર છું, તમારો સ્માર્ট ખેતી સહાયક. આજે હું તમને કેવી રીતે મદદ કરી શકું?",
    "ml": "നമസ്കാരം! ഞാൻ കൃഷിമിത്ര ആണ്, നിങ്ങളുടെ സ്മാർട്ട് കൃഷി സഹായി. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
}


def get_greeting(lang_code: str) -> str:
    return GREETINGS.get(lang_code, GREETINGS["en"])
