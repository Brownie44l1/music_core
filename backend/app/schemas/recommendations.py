from pydantic import BaseModel, Field


class MatchedFeatures(BaseModel):
    genre: str
    energy_level: float = Field(..., ge=0.0, le=1.0)
    tempo: str


class Explanation(BaseModel):
    similar_users: list[str] = Field(default_factory=list)
    matched_features: MatchedFeatures
    confidence: float = Field(..., ge=0.0, le=1.0)


class RecommendedSong(BaseModel):
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
    session_id: str
    recommendations: list[RecommendedSong]
    is_cold_start: bool = False
    algorithm_version: str = "v1"
