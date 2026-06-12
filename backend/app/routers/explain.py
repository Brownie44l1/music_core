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
    import re
    UUID_REGEX = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    if not UUID_REGEX.match(recommendation_id):
        raise HTTPException(
            status_code=400,
            detail=f"'{recommendation_id}' is not in a valid standard hyphenated UUID format",
        )
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

    if song.tempo is None:
        tempo_label = "Unknown"
    elif song.tempo < 80:
        tempo_label = "Low"
    elif song.tempo < 120:
        tempo_label = "Medium"
    else:
        tempo_label = "High"

    # Normalize tempo if it was stored as BPM string in seed data (e.g. "112 BPM")
    stored_tempo = raw_features.get("tempo")
    if stored_tempo and "BPM" in stored_tempo:
        try:
            bpm_val = float(stored_tempo.replace("BPM", "").strip())
            if bpm_val < 80:
                stored_tempo = "Low"
            elif bpm_val < 120:
                stored_tempo = "Medium"
            else:
                stored_tempo = "High"
        except ValueError:
            stored_tempo = tempo_label

    matched_features = MatchedFeatures(
        genre=song.genre,
        energy_level=raw_features.get("energy_level", song.energy_level),
        tempo=stored_tempo or tempo_label,
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