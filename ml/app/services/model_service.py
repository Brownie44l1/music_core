"""
Model Service
──────────────
Orchestrates the full recommendation pipeline:
  1. Fetch user interaction history from DB
  2. Decide: personalised (SVD) or cold start (popularity)?
  3. Generate recommendations
  4. Build explanations for each recommendation
  5. Return structured response

This service is the brain that connects the recommender,
explainer, and cold_start modules together.
"""

from __future__ import annotations

import logging

from app.cold_start import get_cold_start_recommendations, is_cold_start
from app.explainer import build_explanation, build_user_genre_profile
from app.models.schemas import (
    Explanation,
    MatchedFeatures,
    RecommendationResponse,
    RecommendedSong,
)
from app.recommender import MusicRecommender

logger = logging.getLogger(__name__)

# Module-level recommender — loaded once when the service starts
_recommender = MusicRecommender()


class ModelService:
    """
    Orchestrates the recommendation pipeline end-to-end.

    TODO (Ticket 2.1): Load trained model on startup
    TODO (Ticket 3.2): Connect to PostgreSQL for real interaction data
    TODO (Ticket 3.2): Connect to Redis for caching
    """

    async def recommend(
        self,
        session_id: str,
        limit: int = 10,
    ) -> RecommendationResponse:
        """
        Full recommendation pipeline for a user session.

        Args:
            session_id: Browser session identifier
            limit:      Number of recommendations to return

        Returns:
            RecommendationResponse with songs + explanations
        """
        # ── Step 1: Fetch user interactions ──────────────────────────
        # TODO: Replace with real DB query in Ticket 3.2
        interactions = await self._fetch_interactions(session_id)
        interaction_count = len(interactions)

        # ── Step 2: Cold start check ──────────────────────────────────
        if is_cold_start(interaction_count):
            logger.info(
                "Cold start for session %s (%d interactions)",
                session_id,
                interaction_count,
            )
            songs = await self._fetch_popular_songs()
            fallback_songs = get_cold_start_recommendations(songs, limit=limit)
            return self._build_cold_start_response(session_id, fallback_songs)

        # ── Step 3: Personalised recommendations ─────────────────────
        candidate_songs = await self._fetch_candidate_songs(session_id)
        candidate_ids = [s["id"] for s in candidate_songs]
        song_map = {s["id"]: s for s in candidate_songs}

        scored = _recommender.recommend(session_id, candidate_ids, limit=limit)

        # ── Step 4: Build explanations ────────────────────────────────
        user_genre_profile = build_user_genre_profile(interactions)
        similar_users = await self._fetch_similar_users(session_id)

        recommended_songs = []
        for song_id, score in scored:
            song = song_map[song_id]
            explanation_dict = build_explanation(
                user_id=session_id,
                song=song,
                similar_user_ids=similar_users,
                user_genre_profile=user_genre_profile,
            )
            recommended_songs.append(
                RecommendedSong(
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

        return RecommendationResponse(
            session_id=session_id,
            recommendations=recommended_songs,
            is_cold_start=False,
        )

    # ── Private helpers (stubbed — replace with real DB calls) ────────

    async def _fetch_interactions(self, session_id: str) -> list[dict]:
        """TODO Ticket 3.2: Query ListeningEvent + UserFeedback tables."""
        return []

    async def _fetch_popular_songs(self) -> list[dict]:
        """TODO Ticket 3.2: Query Song table ordered by popularity_score."""
        return []

    async def _fetch_candidate_songs(self, session_id: str) -> list[dict]:
        """TODO Ticket 3.2: Songs user has NOT yet heard."""
        return []

    async def _fetch_similar_users(self, session_id: str) -> list[str]:
        """TODO Ticket 2.3: Use SVD latent space to find nearest neighbours."""
        return []

    def _build_cold_start_response(
        self,
        session_id: str,
        songs: list[dict],
    ) -> RecommendationResponse:
        """Build a cold start response from popular songs."""
        recommended = [
            RecommendedSong(
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
            for s in songs
        ]
        return RecommendationResponse(
            session_id=session_id,
            recommendations=recommended,
            is_cold_start=True,
        )
