# DecisionIQ — AI Decision Intelligence Platform

> Real-time consumer signal intelligence powered by LangGraph, Groq LLaMA 3.3, and live data ingestion from Reddit, YouTube, App Store, and Google News. Ranks signals using the HAZRA scoring model, detects emerging trends, forecasts cluster momentum, and surfaces proactive insights through Winston — a RAG-powered conversational AI assistant with executive reporting.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          LIVE DATA SOURCES                              │
│                                                                         │
│   Reddit (JSON API)   YouTube API   App Store Scraper   Google News     │
│        ↓                  ↓               ↓                  ↓         │
│                    APScheduler (BackgroundScheduler)                    │
│           Reddit: 60min │ YouTube: 3hr │ AppStore: 6hr │ GNews: 30min  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                                 │
│                                                                         │
│  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐  │
│  │  Signal Ingest  │   │  HAZRA Scoring   │   │  Brand & Cluster    │  │
│  │  POST /ingest   │──▶│  volume 25%      │   │  Detection          │  │
│  │                 │   │  velocity 30%    │   │  (keyword matching) │  │
│  │  Multimodal:    │   │  sentiment 25%   │   │                     │  │
│  │  text/image/    │   │  recency 20%     │   │  Brands: Samsung    │  │
│  │  video          │   └──────────────────┘   │  Apple, Google      │  │
│  └─────────────────┘                          │  Pixel              │  │
│                                               └─────────────────────┘  │
│  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐  │
│  │  GET /signals   │   │  GET /trends     │   │  POST /forecast     │  │
│  │  /ranked        │   │  7-day rolling   │   │  Holt-Winters       │  │
│  │                 │   │  delta momentum  │   │  Exponential        │  │
│  │  HAZRA ranked   │   │  emerging /      │   │  Smoothing          │  │
│  │  color coded    │   │  declining /     │   │  7 / 14 / 28 days   │  │
│  │  green/amber/   │   │  stable badges   │   │  confidence band    │  │
│  │  red            │   └──────────────────┘   └─────────────────────┘  │
│  └─────────────────┘                                                    │
│  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐  │
│  │  GET            │   │  GET /alerts     │   │  POST /winston/chat │  │
│  │  /competitive   │   │                  │   │                     │  │
│  │                 │   │  LangGraph       │   │  RAG over ranked    │  │
│  │  Multi-brand    │   │  Sentinel Agent  │   │  signals            │  │
│  │  HAZRA timeline │   │  polls every 60s │   │  Session history    │  │
│  │  inflection     │   │  fires on        │   │  Groq LLaMA 3.3     │  │
│  │  points         │   │  HAZRA ≥ thresh  │   │  70B Versatile      │  │
│  └─────────────────┘   └──────────────────┘   └─────────────────────┘  │
│  ┌─────────────────┐   ┌──────────────────┐                            │
│  │  POST /reports  │   │  PATCH /config   │                            │
│  │  /generate      │   │  /threshold      │                            │
│  │                 │   │                  │                            │
│  │  Groq LLaMA     │   │  Configurable    │                            │
│  │  executive      │   │  alert threshold │                            │
│  │  brief markdown │   └──────────────────┘                            │
│  └─────────────────┘                                                    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌───────────────────┐   ┌──────────────────┐
        │   PostgreSQL DB   │   │   Groq LLM API   │
        │                   │   │                  │
        │  signals          │   │  llama-3.3-70b   │
        │  signal_scores    │   │  -versatile      │
        │  alerts           │   │                  │
        │  chat_sessions    │   │  Rate limited:   │
        │  reports          │   │  20 req/min      │
        │  config           │   │  Exp. backoff    │
        └───────────────────┘   └──────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        REACT FRONTEND                                   │
│                                                                         │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Signal Feed  │  │   Trend     │  │   Forecast   │  │ Competitive │ │
│  │              │  │ Detection   │  │    View      │  │  Timeline   │ │
│  │ HAZRA ranked │  │             │  │              │  │             │ │
│  │ cards        │  │ Momentum    │  │ Line chart + │  │ Multi-brand │ │
│  │ green/amber/ │  │ chart       │  │ confidence   │  │ HAZRA lines │ │
│  │ red          │  │ emerging /  │  │ band         │  │ inflection  │ │
│  │              │  │ declining   │  │ LLM narrative│  │ point dots  │ │
│  └──────────────┘  └─────────────┘  └──────────────┘  └─────────────┘ │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐                  │
│  │    Winston   │  │  Executive  │  │    Alert     │                  │
│  │     Chat     │  │   Reports   │  │    Center    │                  │
│  │              │  │             │  │              │                  │
│  │ Persistent   │  │ Markdown    │  │ Live polling │                  │
│  │ session      │  │ report      │  │ Threshold    │                  │
│  │ RAG context  │  │ PDF export  │  │ slider       │                  │
│  │ brand/cluster│  │ clipboard   │  │ Alert history│                  │
│  └──────────────┘  └─────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI |
| AI Agent | LangGraph (5-node Sentinel pipeline) |
| LLM | Groq — llama-3.3-70b-versatile |
| Forecasting | statsmodels Holt-Winters Exponential Smoothing |
| Database | PostgreSQL + SQLAlchemy |
| Task Scheduling | APScheduler |
| Frontend | React + TypeScript + Vite |
| Charts | Recharts |

---

## Features

- **Live Signal Ingestion** — Reddit, YouTube, App Store, Google News polled on schedule
- **HAZRA Scoring** — weighted composite score (volume, velocity, sentiment, recency)
- **Trend Detection** — 7-day rolling delta, emerging/declining/stable cluster badges
- **Forecasting** — Holt-Winters time series with confidence bands and LLM narrative
- **Competitive Intelligence** — multi-brand HAZRA timeline with inflection point detection
- **Winston AI Assistant** — RAG-powered conversational assistant with session memory
- **Executive Reports** — LLM-generated markdown briefs, PDF export
- **Sentinel Alerts** — LangGraph agent polls every 60s, fires on HAZRA threshold breach
- **Alert Center** — live feed with configurable threshold slider

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Groq API key (free at [console.groq.com](https://console.groq.com))
- YouTube Data API key (optional)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ai-decision-intelligence-platform.git
cd ai-decision-intelligence-platform
```

### 2. Configure environment

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://postgres:password@localhost:5432/decisioniq
YOUTUBE_API_KEY=your_key_here   # optional
ALERT_THRESHOLD=75
CORS_ORIGINS=http://localhost:5173
```

### 3. Set up the database

Create the database in PostgreSQL, then run:

```bash
psql -U postgres -d decisioniq -f backend/init_db.sql
```

### 4. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

On first run, seed data is auto-generated.

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Project Structure

```
├── backend/
│   ├── main.py                  # FastAPI app + lifespan
│   ├── database.py              # SQLAlchemy engine + session
│   ├── models.py                # ORM models
│   ├── hazra.py                 # HAZRA score computation
│   ├── llm.py                   # Groq wrapper + rate limiter
│   ├── agents.py                # LangGraph Sentinel agent
│   ├── seed.py                  # Database seeder
│   ├── connectors/
│   │   ├── reddit_connector.py  # Reddit public JSON API
│   │   ├── youtube_connector.py # YouTube Data API
│   │   ├── appstore_connector.py# App Store scraper
│   │   ├── gnews_connector.py   # Google News
│   │   ├── brand_detector.py    # Keyword brand/cluster detection
│   │   ├── ingest_helper.py     # Shared ingest logic
│   │   └── scheduler.py        # APScheduler setup
│   └── routers/
│       ├── ingest.py
│       ├── signals.py
│       ├── trends.py
│       ├── forecast.py
│       ├── competitive.py
│       ├── alerts.py
│       ├── winston.py
│       ├── reports.py
│       └── config.py
└── frontend/
    └── src/
        ├── App.tsx
        ├── api.ts
        └── components/
            ├── SignalFeed.tsx
            ├── TrendDetection.tsx
            ├── ForecastView.tsx
            ├── CompetitiveTimeline.tsx
            ├── WinstonChat.tsx
            ├── ExecutiveReports.tsx
            └── AlertCenter.tsx
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `ALERT_THRESHOLD` | No | Default HAZRA alert threshold (default: 75) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `YOUTUBE_API_KEY` | No | YouTube Data API v3 key |

---

## License

MIT
