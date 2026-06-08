import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.recommendation import Recommendation
from app.models.song import Song
from app.models.artist import Artist
from app.schemas.explain import ExplainResponse
from app.schemas.recommendations import Explanation, MatchedFeatures

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/explain", response_model=ExplainResponse)
async def explain_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
) -> ExplainResponse:
    """
    Return the explanation for a previously served recommendation.
    Reads explanation JSONB from Recommendation table, enriched with
    Song and Artist data.
    """
    # ── Parse and validate the UUID ───────────────────────────────────
    try:
        rec_uuid = uuid.UUID(recommendation_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"'{recommendation_id}' is not a valid recommendation ID",
        )

    # ── Fetch recommendation + song + artist in one join ──────────────
    result = (
        db.query(Recommendation, Song, Artist)
        .join(Song, Recommendation.song_id == Song.id)
        .join(Artist, Song.artist_id == Artist.id)
        .filter(Recommendation.id == rec_uuid)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation '{recommendation_id}' not found",
        )

    rec, song, artist = result

    # ── Build explanation from stored JSONB ───────────────────────────
    # Enrich matched_features with live song data so the response always
    # reflects the actual stored values, not just whatever the ML wrote.
    raw = rec.explanation or {}
    raw_features = raw.get("matched_features", {})

    matched_features = MatchedFeatures(
        genre=song.genre,
        energy_level=raw_features.get("energy_level", song.energy_level),
        tempo=raw_features.get("tempo", f"{int(song.tempo)} BPM"),
    )

    explanation = Explanation(
        similar_users=raw.get("similar_users", []),
        matched_features=matched_features,
        confidence=raw.get("confidence", rec.score),
    )

    logger.info("Explanation served for recommendation %s", recommendation_id)

    return ExplainResponse(
        recommendation_id=str(rec.id),
        song_id=str(song.id),
        title=song.title,
        artist=artist.name,
        explanation=explanation,
    )