"""
plugd ML Engine
────────────────────
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommend
from app.services.model_service import _recommender
from app.recommender import MODEL_PATH

app = FastAPI(
    title="plugd ML Engine",
    description="Collaborative filtering recommendation engine for Nigerian music",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/ml", tags=["recommendations"])


@app.on_event("startup")
async def load_model() -> None:
    """Load the trained SVD model on startup."""
    try:
        _recommender.load(MODEL_PATH)
        print(f"✅ SVD model loaded from {MODEL_PATH}")
    except FileNotFoundError:
        print(f"⚠️  No model found at {MODEL_PATH} — cold start only mode")


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {
        "status": "ok",
        "service": "plugd_ml",
        "model_loaded": _recommender.is_trained,
    }
