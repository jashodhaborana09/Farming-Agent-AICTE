"""
Smart Farming AI Agent — Configuration
IBM Granite via watsonx.ai + RAG pipeline settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── IBM watsonx.ai ───────────────────────────────────────────────────────────
WATSONX_API_KEY   = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL       = os.getenv("WATSONX_URL", "https://eu-gb.ml.cloud.ibm.com")

# Model IDs available on IBM Cloud Lite (eu-gb region)
# LLM: best available text-generation model on this region
GRANITE_LLM_MODEL   = "meta-llama/llama-3-3-70b-instruct"
# Embedding: IBM Granite multilingual embedding (supports Indian languages)
GRANITE_EMBED_MODEL = "ibm/granite-embedding-278m-multilingual"

# Granite generation parameters
GRANITE_PARAMS = {
    "decoding_method": "greedy",
    "max_new_tokens": 1024,
    "min_new_tokens": 10,
    "stop_sequences": [],
    "repetition_penalty": 1.1,
    "temperature": 0.3,
}

# ─── Vector Store ─────────────────────────────────────────────────────────────
CHROMA_DB_PATH    = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
COLLECTION_NAME   = "farming_knowledge"
RETRIEVAL_TOP_K   = 5

# ─── External APIs ────────────────────────────────────────────────────────────
OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
AGMARKET_API_KEY    = os.getenv("AGMARKET_API_KEY", "")
AGMARKET_BASE_URL   = os.getenv("AGMARKET_BASE_URL",
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070")

# ─── Multilingual Support ─────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "mr": "Marathi",
    "pa": "Punjabi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
}

# ─── App ──────────────────────────────────────────────────────────────────────
APP_HOST  = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT  = int(os.getenv("APP_PORT", "8000"))
DEBUG     = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
