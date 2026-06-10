from fastapi import APIRouter, HTTPException, Query

from app.schemas.songs import SongListResponse

router = APIRouter()


@router.get("/songs", response_model=SongListResponse)
async def get_songs(
    genre: str | None = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    Browse songs, optionally filtered by genre.
    TODO (Ticket 4.4): Implement — query Song table.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
