# 🌾 KrishiMitra — AI Agent for Smart Farming Advice

> **IBM Granite + watsonx.ai · RAG Pipeline · 10 Indian Languages · Real-time Data**

KrishiMitra ("Farm Friend") is a RAG-powered AI Agent that delivers real-time, localised agricultural guidance to small-scale Indian farmers. Powered by **IBM Granite** via **IBM Cloud watsonx.ai**, it bridges the knowledge gap with timely, data-driven decisions.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🤖 **IBM Granite LLM** | `ibm/granite-13b-chat-v2` via watsonx.ai (Cloud Lite) |
| 📚 **RAG Pipeline** | ChromaDB + IBM `slate-125m-english-rtrvr` embeddings |
| 🌐 **10 Languages** | EN, HI, TA, TE, KN, MR, PA, BN, GU, ML |
| 🌤 **Live Weather** | Open-Meteo API (free, no key) — 7-day farm-specific forecast |
| 💰 **Mandi Prices** | Agmarknet (data.gov.in) + MSP 2024-25 fallback |
| 🌱 **Crop Advisor** | Season + soil-type matched crop recommendations |
| 🐛 **Pest Control** | Crop-specific integrated pest management guidance |
| 🏛 **Govt Schemes** | PM-KISAN, Fasal Bima, eNAM, KCC, PMKSY & more |
| 🎙 **Voice Input** | Web Speech API (Chrome) with Indian language support |
| ⚡ **Real-time WS** | WebSocket endpoint for streaming chat |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Farmer (any device)                   │
│          asks in Hindi / Telugu / English / …            │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP / WebSocket
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Application (main.py)               │
│  /api/chat  /api/weather  /api/market  /api/crops  /ws  │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   FarmingAgent (agent/)      │
          │  1. Detect Language          │
          │  2. Translate → English      │
          │  3. Classify Intent          │
          │  4. Invoke Tool(s)           │
          │  5. RAG Pipeline             │
          │  6. Translate ← English      │
          └──────┬───────────┬──────────┘
                 │           │
    ┌────────────▼──┐   ┌───▼──────────────────────┐
    │  Tools Layer  │   │     RAG Pipeline (rag/)    │
    │               │   │                            │
    │ 🌤 Weather    │   │  ChromaDB Vector Store     │
    │ 💰 Market     │   │  (farming knowledge base)  │
    │ 🌱 Crops      │   │         ↕                  │
    │ 🌐 Language   │   │  IBM Granite Embeddings    │
    └───────────────┘   │  slate-125m-english-rtrvr  │
                        │         ↕                  │
                        │  IBM Granite LLM           │
                        │  granite-13b-chat-v2       │
                        │  (via watsonx.ai)          │
                        └────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <repo-url>
cd farming-agent
pip install -r requirements.txt
```

### 2. Configure IBM Cloud Credentials

```bash
cp .env.example .env
# Edit .env with your credentials:
# WATSONX_API_KEY=<your IBM Cloud API key>
# WATSONX_PROJECT_ID=<your watsonx.ai project ID>
```

**Get credentials:**
1. Create a free account at [cloud.ibm.com](https://cloud.ibm.com)
2. Create a **watsonx.ai** project at [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
3. Generate an API key: IBM Cloud → Manage → Access → API Keys
4. Copy your Project ID from the watsonx.ai project settings

### 3. Ingest Knowledge Base

```bash
python scripts/ingest.py
```

### 4. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open the App

Visit **http://localhost:8000** in your browser.

---

## 📁 Project Structure

```
farming-agent/
├── main.py                   # FastAPI app, all API endpoints
├── config.py                 # Configuration (IBM, DB, App)
├── requirements.txt
├── .env.example
│
├── agent/
│   └── farming_agent.py      # Main orchestration layer
│
├── rag/
│   ├── granite_client.py     # IBM Granite LLM + Embeddings client
│   ├── rag_pipeline.py       # RAG prompt building + generation
│   └── vector_store.py       # ChromaDB vector store
│
├── tools/
│   ├── weather_service.py    # Open-Meteo weather forecasts
│   ├── market_service.py     # Agmarknet / MSP mandi prices
│   ├── crop_service.py       # Crop recommendation engine
│   └── language_service.py   # Language detection + translation
│
├── data/
│   ├── knowledge_base.py     # Curated farming documents
│   └── chroma_db/            # Persistent vector store (auto-created)
│
├── frontend/
│   ├── index.html            # Main chat UI
│   └── static/
│       └── style.css
│
└── scripts/
    ├── ingest.py             # One-time knowledge base ingestion
    └── test_services.py      # Smoke tests
```

---

## 🧠 IBM Granite Models Used

| Role | Model ID |
|---|---|
| Chat / Generation | `ibm/granite-13b-chat-v2` |
| Embeddings | `ibm/slate-125m-english-rtrvr` |

Both models are available on **IBM Cloud Lite** (free tier) via [watsonx.ai](https://dataplatform.cloud.ibm.com).

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Main chat with natural language query |
| `POST` | `/api/weather` | Get 7-day weather forecast |
| `POST` | `/api/market` | Get mandi price for a commodity |
| `POST` | `/api/crops` | Crop recommendations |
| `GET` | `/api/languages` | List supported languages |
| `WS` | `/ws/chat` | Real-time WebSocket chat |

### Chat Request Example

```json
POST /api/chat
{
  "message": "Which crop is best for black soil in this season?",
  "language": "en",
  "city": "Nagpur",
  "soil_type": "black"
}
```

---

## 🔧 Test Services

```bash
# Test without IBM (weather, market, crop, language)
python scripts/test_services.py

# Full test including IBM Granite (requires .env credentials)
python scripts/test_services.py --with-ibm
```

---

## 📊 Sample Queries

| Language | Query |
|---|---|
| English | "What crop is best for this season?" |
| English | "What is today's mandi rate for tomatoes?" |
| Hindi | "धान की फसल में कौन सा खाद डालें?" |
| Telugu | "నా పంటకు ఏ పురుగుమందు వాడాలి?" |
| Marathi | "आज गव्हाचा मंडी भाव काय आहे?" |
| Punjabi | "ਕਣਕ ਦੀ ਫਸਲ ਲਈ ਖਾਦ ਕਦੋਂ ਪਾਉਣੀ ਚਾਹੀਦੀ ਹੈ?" |

---

## 🏛 Government Data Sources

- **Agmarknet**: [agmarknet.gov.in](https://agmarknet.gov.in) — live mandi prices
- **data.gov.in**: National Agriculture Market dataset
- **PM-KISAN**: [pmkisan.gov.in](https://pmkisan.gov.in)
- **eNAM**: [enam.gov.in](https://enam.gov.in)
- **PMKSY**: [pmksy.gov.in](https://pmksy.gov.in)

---

## 📄 License

MIT License — free for academic and non-commercial use.
