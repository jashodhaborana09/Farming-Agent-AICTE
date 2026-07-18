"""
FastAPI Application — KrishiMitra Smart Farming AI Agent
REST + WebSocket endpoints for farmer queries
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Startup/Shutdown ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ingest knowledge base on startup."""
    logger.info("🌱 KrishiMitra starting up…")
    try:
        from rag.vector_store import vector_store
        vector_store.ingest()
        logger.info("✅ Knowledge base ready.")
    except Exception as exc:
        logger.warning("Knowledge base ingestion skipped (IBM credentials not set?): %s", exc)
    yield
    logger.info("KrishiMitra shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="KrishiMitra — Smart Farming AI Agent",
    description="RAG-powered farming advisor using IBM Granite (watsonx.ai)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for the frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# ── Pydantic Models ───────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message:   str             = Field(..., min_length=1, max_length=2000)
    language:  Optional[str]   = None
    city:      Optional[str]   = None
    soil_type: Optional[str]   = None


class ChatResponse(BaseModel):
    answer:        str
    intent:        str
    language:      str
    tool_data:     dict = {}
    sources:       list = []


class WeatherRequest(BaseModel):
    city: Optional[str]  = None
    lat:  Optional[float] = None
    lon:  Optional[float] = None


class MarketRequest(BaseModel):
    commodity: str
    state:     Optional[str] = None


class CropRequest(BaseModel):
    soil_type:          Optional[str]   = None
    season:             Optional[str]   = None
    water_availability: Optional[str]   = None
    location:           Optional[str]   = None
    area_acres:         Optional[float] = None


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("frontend/index.html")


@app.get("/health")
async def health():
    return {"status": "ok", "app": "KrishiMitra", "version": "1.0.0"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint — processes a farmer's natural language question.
    Supports 10 Indian languages + English.
    """
    from agent.farming_agent import farming_agent
    try:
        result = await farming_agent.chat(
            user_message=req.message,
            language=req.language,
            city=req.city,
            soil_type=req.soil_type,
        )
        return ChatResponse(
            answer=result["answer"],
            intent=result["intent"],
            language=result["original_lang"],
            tool_data=result.get("tool_data", {}),
            sources=result.get("sources", []),
        )
    except Exception as exc:
        logger.error("Chat error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/weather")
async def weather(req: WeatherRequest):
    """Fetch 7-day weather forecast for a city or coordinates."""
    from tools.weather_service import get_weather
    return await get_weather(city=req.city, lat=req.lat, lon=req.lon)


@app.post("/api/market")
async def market(req: MarketRequest):
    """Fetch mandi prices for a commodity."""
    from tools.market_service import get_market_prices
    return await get_market_prices(commodity=req.commodity, state=req.state)


@app.post("/api/crops")
async def crops(req: CropRequest):
    """Get crop recommendations based on soil and season."""
    from tools.crop_service import recommend_crops
    return recommend_crops(
        soil_type=req.soil_type,
        season=req.season,
        water_availability=req.water_availability,
        location=req.location,
        area_acres=req.area_acres,
    )


@app.get("/api/languages")
async def languages():
    """List all supported languages."""
    return config.SUPPORTED_LANGUAGES


@app.get("/api/greeting/{lang_code}")
async def greeting(lang_code: str):
    """Get localised greeting in the requested language."""
    from tools.language_service import get_greeting
    return {"greeting": get_greeting(lang_code), "language": lang_code}


# ── WebSocket for real-time chat ──────────────────────────────────────────────
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat with the farming agent."""
    await websocket.accept()
    logger.info("WebSocket connection opened.")
    from agent.farming_agent import farming_agent
    try:
        while True:
            data = await websocket.receive_json()
            message   = data.get("message", "")
            language  = data.get("language")
            city      = data.get("city")
            soil_type = data.get("soil_type")

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            await websocket.send_json({"status": "processing", "message": "Thinking…"})
            try:
                result = await farming_agent.chat(
                    user_message=message,
                    language=language,
                    city=city,
                    soil_type=soil_type,
                )
                await websocket.send_json({"status": "done", **result})
            except Exception as exc:
                await websocket.send_json({"status": "error", "message": str(exc)})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.APP_HOST, port=config.APP_PORT, reload=config.DEBUG)
