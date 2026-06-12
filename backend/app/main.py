from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import recommendations, feedback, songs, explain
from app.db import engine, Base

# Import all models so Base knows about them
from app.models import user, user_feedback, song, artist, recommendation, listening_event  # noqa: F401

app = FastAPI(
    title="plugd Backend API",
    description="API layer for the Nigerian music recommendation system",
    version="0.1.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(songs.router, prefix="/api", tags=["songs"])
app.include_router(explain.router, prefix="/api", tags=["explain"])


@app.on_event("startup")
async def create_tables() -> None:
    """Create all DB tables on startup if they don't exist."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok", "service": "plugd_backend"}
