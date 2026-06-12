import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.cache import get_cache
from app.db import get_db
from app.models.song import Song
from app.models.user import User
from app.models.user_feedback import UserFeedback
from app.schemas.feedback import FeedbackRequest, FeedbackResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    cache=Depends(get_cache),
) -> FeedbackResponse:
    """
    Record user feedback (like/dislike/skip) for a song.
    - Creates user record if first interaction
    - Looks up song by deezer_track_id
    - Writes feedback to PostgreSQL
    - Invalidates Redis cache so next recs reflect the feedback
    """
    # ── Look up song by deezer_track_id ───────────────────────────────
    # song_id from frontend is the Deezer string ID e.g. "ng_2504834531"
    if not body.song_id.startswith("ng_"):
        raise HTTPException(
            status_code=400,
            detail="song_id must start with the 'ng_' prefix",
        )
    deezer_id = body.song_id.removeprefix("ng_")
    song = db.query(Song).filter(Song.deezer_track_id == deezer_id).first()
    if not song:
        raise HTTPException(
            status_code=404,
            detail=f"Song '{body.song_id}' not found in database",
        )

    # ── Get or create user ────────────────────────────────────────────
    user = db.query(User).filter(User.session_id == body.session_id).first()
    if not user:
        from sqlalchemy.exc import IntegrityError
        try:
            with db.begin_nested():
                user = User(session_id=body.session_id)
                db.add(user)
            db.flush()
            logger.info("Created new user for session %s", body.session_id)
        except IntegrityError:
            user = db.query(User).filter(User.session_id == body.session_id).first()

    # ── Write feedback ────────────────────────────────────────────────
    feedback = db.query(UserFeedback).filter(
        UserFeedback.user_id == user.id,
        UserFeedback.song_id == song.id
    ).first()

    if feedback:
        feedback.feedback_type = body.feedback_type
        logger.info("Feedback updated for user %s on song %s", user.id, song.id)
    else:
        feedback = UserFeedback(
            user_id=user.id,
            song_id=song.id,
            feedback_type=body.feedback_type,
        )
        db.add(feedback)
        logger.info("Feedback created for user %s on song %s", user.id, song.id)
    db.commit()
    logger.info(
        "Feedback recorded: session=%s song=%s type=%s",
        body.session_id,
        body.song_id,
        body.feedback_type,
    )

    # ── Invalidate Redis cache ────────────────────────────────────────
    try:
        import re
        escaped_session_id = re.sub(r'([*?\[\]\\])', r'\\\1', body.session_id)
        pattern = f"recommendations:{escaped_session_id}:*"
        keys = await cache.keys(pattern)
        if keys:
            await cache.delete(*keys)
            logger.info(
                "Cache invalidated for session %s (%d keys)",
                body.session_id,
                len(keys),
            )
    except Exception as e:
        logger.warning("Cache invalidation failed: %s", e)

    return FeedbackResponse(status="ok", message="Feedback recorded")
