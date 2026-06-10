"""
Pydantic schemas for the ML engine API.
These define the shape of requests and responses.
"""

from uuid import UUID
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request body for generating recommendations."""

    session_id: str = Field(..., min_length=1, max_length=255, description="Browser session identifier")
    limit: int = Field(default=10, ge=1, le=50, description="Number of recommendations")

    model_config = {"json_schema_extra": {"example": {"session_id": "abc-123", "limit": 10}}}


class MatchedFeatures(BaseModel):
    """Features that drove a recommendation — used for explainability."""

    genre: str
    energy_level: float = Field(..., ge=0.0, le=1.0)
    tempo: str  # "Low" | "Medium" | "High"


class Explanation(BaseModel):
    """Why a song was recommended."""

    similar_users: list[str] = Field(default_factory=list)
    matched_features: MatchedFeatures
    confidence: float = Field(..., ge=0.0, le=1.0)


class RecommendedSong(BaseModel):
    """A single recommended song with its explanation."""

    recommendation_id: str
    song_id: str
    title: str
    artist: str
    genre: str
    score: float = Field(..., ge=0.0, le=1.0)
    preview_url: str | None = None
    album_art_url: str | None = None
    explanation: Explanation


class RecommendationResponse(BaseModel):
    """Full response from the recommendation endpoint."""

    session_id: str
    recommendations: list[RecommendedSong]
    is_cold_start: bool = Field(
        default=False,
        description="True if user had insufficient history — fallback was used",
    )
    algorithm_version: str = Field(default="v1")
