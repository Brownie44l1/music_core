"""
music_core ML Engine
────────────────────
FastAPI application entry point.
This service exposes the recommendation model via HTTP.
The backend service calls this internally.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommend

app = FastAPI(
    title="music_core ML Engine",
    description="Collaborative filtering recommendation engine for Nigerian music",
    version="0.1.0",
    docs_url="/docs",
)

# CORS — only the backend service should call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(recommend.router, prefix="/ml", tags=["recommendations"])


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Basic health check. Render.com uses this to verify the service is up."""
    return {"status": "ok", "service": "music_core_ml"}
