import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from seed import seed
from agents import run_sentinel_loop
from connectors.scheduler import start_scheduler, stop_scheduler
from routers import ingest, signals, trends, forecast, competitive, alerts, winston, reports, config

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    start_scheduler()
    asyncio.create_task(run_sentinel_loop())
    yield
    stop_scheduler()

app = FastAPI(title="AI Decision Intelligence Platform", lifespan=lifespan)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(signals.router)
app.include_router(trends.router)
app.include_router(forecast.router)
app.include_router(competitive.router)
app.include_router(alerts.router)
app.include_router(winston.router)
app.include_router(reports.router)
app.include_router(config.router)

@app.get("/health")
def health():
    return {"status": "ok"}
