"""Al-Syaka Quant AI — Main FastAPI Application."""

from contextlib import asynccontextmanager

from al_syaka_common.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from src.routers import ai as ai_router
from src.routers import backtesting as bt_router
from src.routers import indicators as indicators_router
from src.routers import market_data
from src.routers import market_structure as ms_router
from src.routers import mt5 as mt5_router
from src.routers import paper_trading as pt_router
from src.routers import settings as settings_router
from src.routers import signals
from src.routers import unified_signal as us_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    print(f"🚀 Al-Syaka Quant AI API starting... (log_level={settings.log_level})")
    yield
    # Shutdown
    print("👋 Al-Syaka Quant AI API shutting down...")


app = FastAPI(
    title="Al-Syaka Quant AI API",
    description="AI-powered Market Intelligence & Trading Signal Platform",
    version="0.3.0",
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# --- Routers ---
app.include_router(market_data.router)
app.include_router(signals.router)
app.include_router(indicators_router.router)
app.include_router(ms_router.router)
app.include_router(bt_router.router)
app.include_router(ai_router.router)
app.include_router(pt_router.router)
app.include_router(mt5_router.router)
app.include_router(settings_router.router)
app.include_router(us_router.router)


# --- Root Health Check ---
@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "ok",
        "service": "al-syaka-quant-ai",
        "version": "0.2.0",
        "sprint": "Sprint 2 — Analytical Engine",
    }


@app.get("/", tags=["system"])
async def root():
    return {
        "message": "Al-Syaka Quant AI API",
        "version": "0.2.0",
        "sprint": "Sprint 2 — Analytical Engine",
        "docs": "/docs",
    }
