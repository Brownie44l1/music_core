from pydantic import BaseModel, Field


class SongResponse(BaseModel):
    id: str
    title: str
    artist: str
    genre: str
    energy_level: float = Field(..., ge=0.0, le=1.0)
    tempo: float
    popularity_score: float
    preview_url: str | None = None
    album_art_url: str | None = None
    is_synthetic: bool = False


class SongListResponse(BaseModel):
    songs: list[SongResponse]
    total: int
