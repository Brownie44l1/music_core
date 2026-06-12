"""
Model Service
──────────────
Orchestrates the full recommendation pipeline:
  1. Fetch user interaction history from DB
  2. Decide: personalised (SVD) or cold start (popularity)?
  3. Generate recommendations
  4. Build explanations for each recommendation
  5. Return structured response
"""

from __future__ import annotations

import logging

from sqlalchemy import text

from app.cold_start import get_cold_start_recommendations, is_cold_start
from app.db import SessionLocal
from app.explainer import build_explanation, build_user_genre_profile
from app.models.schemas import (
    Explanation,
    MatchedFeatures,
    RecommendationResponse,
    RecommendedSong,
)
from app.recommender import MusicRecommender

logger = logging.getLogger(__name__)

_recommender = MusicRecommender()

# Feedback weights used to derive an implicit rating (0–5 scale)
_FEEDBACK_WEIGHT = {"like": 4.0, "dislike": 1.0, "skip": 2.0}
_COMPLETION_BONUS = 1.0   # added when play was completed
_BASE_PLAY_RATING = 2.5   # rating for any play event with no feedback


class ModelService:
    """Orchestrates the recommendation pipeline end-to-end."""

    async def recommend(
        self,
        session_id: str,
        limit: int = 10,
    ) -> RecommendationResponse:
        import uuid
        # ── Ensure user exists in database ──────────────────────────────────
        with SessionLocal() as db:
            user_row = db.execute(
                text("SELECT id FROM users WHERE session_id = :session_id"),
                {"session_id": session_id}
            ).fetchone()
            if not user_row:
                user_uuid = uuid.uuid4()
                db.execute(
                    text("INSERT INTO users (id, session_id, onboarding_done, created_at) VALUES (:id, :session_id, false, NOW()) ON CONFLICT (session_id) DO NOTHING"),
                    {"id": str(user_uuid), "session_id": session_id}
                )
                db.commit()
                # Re-fetch user ID to handle concurrency cleanly
                user_row = db.execute(
                    text("SELECT id FROM users WHERE session_id = :session_id"),
                    {"session_id": session_id}
                ).fetchone()
            user_id = user_row[0]

        interactions = await self._fetch_interactions(session_id)
        interaction_count = len(interactions)

        if is_cold_start(interaction_count):
            logger.info(
                "Cold start for session %s (%d interactions)",
                session_id,
                interaction_count,
            )
            songs = await self._fetch_popular_songs()
            fallback_songs = get_cold_start_recommendations(songs, limit=limit)
            return await self._build_cold_start_response(session_id, user_id, fallback_songs)

        candidate_songs = await self._fetch_candidate_songs(session_id)
        candidate_ids = [s["id"] for s in candidate_songs]
        song_map = {s["id"]: s for s in candidate_songs}

        scored = _recommender.recommend(session_id, candidate_ids, limit=limit)

        # Normalise scores to [0, 1] — SVD raw predictions can exceed 1.0
        if scored:
            min_score = min(s for _, s in scored)
            max_score = max(s for _, s in scored)
            score_range = max_score - min_score or 1.0
            scored = [(sid, round((s - min_score) / score_range, 3)) for sid, s in scored]

        user_genre_profile = build_user_genre_profile(interactions)
        similar_users = await self._fetch_similar_users(session_id)

        recommended_songs = []
        with SessionLocal() as db:
            for song_id, score in scored:
                song = song_map[song_id]
                explanation_dict = build_explanation(
                    user_id=session_id,
                    song=song,
                    similar_user_ids=similar_users,
                    user_genre_profile=user_genre_profile,
                )
                rec_id = uuid.uuid4()
                
                # Write recommendation to DB
                import json
                db.execute(
                    text("""
                        INSERT INTO recommendations (id, user_id, song_id, score, explanation, algorithm_version, served_at, interacted)
                        VALUES (:id, :user_id, :song_id, :score, CAST(:explanation AS jsonb), :algo, NOW(), false)
                    """),
                    {
                        "id": str(rec_id),
                        "user_id": str(user_id),
                        "song_id": song_id,
                        "score": round(score, 3),
                        "explanation": json.dumps(explanation_dict),
                        "algo": "svd-v1"
                    }
                )
                
                recommended_songs.append(
                    RecommendedSong(
                        recommendation_id=str(rec_id),
                        song_id=song_id,
                        title=song["title"],
                        artist=song["artist"],
                        genre=song["genre"],
                        score=round(score, 3),
                        preview_url=song.get("preview_url"),
                        album_art_url=song.get("album_art_url"),
                        explanation=Explanation(
                            similar_users=explanation_dict["similar_users"],
                            matched_features=MatchedFeatures(
                                **explanation_dict["matched_features"]
                            ),
                            confidence=explanation_dict["confidence"],
                        ),
                    )
                )
            db.commit()

        return RecommendationResponse(
            session_id=session_id,
            recommendations=recommended_songs,
            is_cold_start=False,
        )

    # ── Private helpers ───────────────────────────────────────────────

    async def _fetch_interactions(self, session_id: str) -> list[dict]:
        """
        Return a combined list of listening events + feedback for this session,
        shaped for build_user_genre_profile() and SVD rating derivation.

        Each dict has: user_id, song_id, song_genre, play_duration_sec, rating
        """
        with SessionLocal() as db:
            rows = db.execute(
                text("""
                    SELECT
                        le.user_id::text,
                        le.song_id::text,
                        s.genre          AS song_genre,
                        le.play_duration_sec,
                        le.completed,
                        uf.feedback_type
                    FROM listening_events le
                    JOIN users   u ON u.id = le.user_id
                    JOIN songs   s ON s.id = le.song_id
                    LEFT JOIN user_feedback uf
                           ON uf.user_id = le.user_id
                          AND uf.song_id = le.song_id
                    WHERE u.session_id = :session_id
                    ORDER BY le.created_at DESC
                    LIMIT 500
                """),
                {"session_id": session_id},
            ).fetchall()

        interactions = []
        for row in rows:
            # Derive an implicit rating from play behaviour + explicit feedback
            base = _FEEDBACK_WEIGHT.get(row.feedback_type, _BASE_PLAY_RATING)
            rating = min(5.0, base + (_COMPLETION_BONUS if row.completed else 0.0))

            interactions.append({
                "user_id": row.user_id,
                "song_id": row.song_id,
                "song_genre": row.song_genre,
                "play_duration_sec": row.play_duration_sec,
                "rating": rating,
            })

        return interactions

    async def _fetch_popular_songs(self) -> list[dict]:
        """
        Return all songs ordered by popularity_score descending,
        joined with artist name — used for cold start fallback.
        """
        with SessionLocal() as db:
            rows = db.execute(
                text("""
                    SELECT
                        s.id::text,
                        s.title,
                        a.name           AS artist,
                        s.genre,
                        s.energy_level,
                        s.tempo,
                        s.popularity_score,
                        s.preview_url,
                        s.album_art_url
                    FROM songs s
                    JOIN artists a ON a.id = s.artist_id
                    ORDER BY s.popularity_score DESC
                """),
            ).fetchall()

        return [dict(row._mapping) for row in rows]

    async def _fetch_candidate_songs(self, session_id: str) -> list[dict]:
        """
        Return songs the user has NOT yet heard, joined with artist name.
        These are the candidates the SVD model will score.
        """
        with SessionLocal() as db:
            rows = db.execute(
                text("""
                    SELECT
                        s.id::text,
                        s.title,
                        a.name           AS artist,
                        s.genre,
                        s.energy_level,
                        s.tempo,
                        s.popularity_score,
                        s.preview_url,
                        s.album_art_url
                    FROM songs s
                    JOIN artists a ON a.id = s.artist_id
                    WHERE s.id NOT IN (
                        SELECT le.song_id
                        FROM listening_events le
                        JOIN users u ON u.id = le.user_id
                        WHERE u.session_id = :session_id
                    )
                    ORDER BY s.popularity_score DESC
                """),
                {"session_id": session_id},
            ).fetchall()

        return [dict(row._mapping) for row in rows]

    async def _fetch_similar_users(self, session_id: str) -> list[str]:
        """
        Ticket 2.3: Find users with similar taste using SVD latent space
        cosine similarity. Falls back to co-like query for new users not
        yet in the trainset.
        """
        # ── Attempt SVD nearest neighbours ───────────────────────────
        with SessionLocal() as db:
            all_users = db.execute(
                text("SELECT session_id FROM users WHERE session_id != :sid"),
                {"sid": session_id},
            ).fetchall()

        all_user_ids = [row.session_id for row in all_users]
        svd_neighbours = _recommender.find_similar_users(
            user_id=session_id,
            all_user_ids=all_user_ids,
            limit=5,
        )

        if svd_neighbours:
            logger.debug(
                "SVD neighbours for %s: %s", session_id, svd_neighbours
            )
            return svd_neighbours

        # ── Fallback: co-like query for users not in trainset ─────────
        logger.debug("Falling back to co-like for %s", session_id)
        with SessionLocal() as db:
            rows = db.execute(
                text("""
                    SELECT DISTINCT u2.session_id
                    FROM user_feedback uf1
                    JOIN users u1 ON u1.id = uf1.user_id
                    JOIN user_feedback uf2
                           ON uf2.song_id = uf1.song_id
                          AND uf2.feedback_type = 'like'
                    JOIN users u2 ON u2.id = uf2.user_id
                    WHERE u1.session_id = :session_id
                      AND u2.session_id != :session_id
                      AND uf1.feedback_type = 'like'
                    LIMIT 5
                """),
                {"session_id": session_id},
            ).fetchall()

        return [row.session_id for row in rows]

    async def _build_cold_start_response(
        self,
        session_id: str,
        user_id: str,
        songs: list[dict],
    ) -> RecommendationResponse:
        import uuid
        import json
        recommended = []
        with SessionLocal() as db:
            for s in songs:
                rec_id = uuid.uuid4()
                explanation_dict = {
                    "similar_users": [],
                    "matched_features": {
                        "genre": s["genre"],
                        "energy_level": s.get("energy_level", 0.5),
                        "tempo": "Medium",
                    },
                    "confidence": s.get("popularity_score", 0.5),
                }
                
                # Write cold start recommendation to DB
                db.execute(
                    text("""
                        INSERT INTO recommendations (id, user_id, song_id, score, explanation, algorithm_version, served_at, interacted)
                        VALUES (:id, :user_id, :song_id, :score, CAST(:explanation AS jsonb), :algo, NOW(), false)
                    """),
                    {
                        "id": str(rec_id),
                        "user_id": str(user_id),
                        "song_id": s["id"],
                        "score": s.get("popularity_score", 0.5),
                        "explanation": json.dumps(explanation_dict),
                        "algo": "svd-v1"
                    }
                )
                
                recommended.append(
                    RecommendedSong(
                        recommendation_id=str(rec_id),
                        song_id=s["id"],
                        title=s["title"],
                        artist=s["artist"],
                        genre=s["genre"],
                        score=s.get("popularity_score", 0.5),
                        preview_url=s.get("preview_url"),
                        album_art_url=s.get("album_art_url"),
                        explanation=Explanation(
                            similar_users=[],
                            matched_features=MatchedFeatures(
                                genre=s["genre"],
                                energy_level=s.get("energy_level", 0.5),
                                tempo="Medium",
                            ),
                            confidence=s.get("popularity_score", 0.5),
                        ),
                    )
                )
            db.commit()
            
        return RecommendationResponse(
            session_id=session_id,
            recommendations=recommended,
            is_cold_start=True,
        )
