from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.song import Song
from app.schemas.songs import SongListResponse, SongResponse

router = APIRouter()


@router.get("/songs", response_model=SongListResponse)
async def get_songs(
    genre: str | None = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Browse songs, optionally filtered by genre.
    """
    query = db.query(Song)
    if genre and genre != "All":
        query = query.filter(Song.genre == genre)
    
    total = query.count()
    
    # Order by popularity_score descending (these are popular songs)
    songs = query.order_by(Song.popularity_score.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    song_responses = []
    for s in songs:
        artist_name = s.artist.name if s.artist else "Unknown Artist"
        song_id = f"ng_{s.deezer_track_id}" if s.deezer_track_id else str(s.id)
        
        song_responses.append(
            SongResponse(
                id=song_id,
                title=s.title,
                artist=artist_name,
                genre=s.genre,
                energy_level=s.energy_level,
                tempo=s.tempo,
                popularity_score=s.popularity_score,
                preview_url=s.preview_url,
                album_art_url=s.album_art_url,
                is_synthetic=s.is_synthetic,
            )
        )
        
    return SongListResponse(songs=song_responses, total=total)
