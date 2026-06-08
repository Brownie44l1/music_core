"""
Explainability Generator
─────────────────────────
Generates human-readable explanations for each recommendation.

This is the XAI (Explainable AI) layer of music_core.
For every recommended song, we explain:
  1. Which similar users also liked this song
  2. Which audio features matched the user's taste profile
  3. A confidence score (0.0 – 1.0)

The explanation is stored as JSONB in the Recommendation table
so it can be served instantly without recomputation.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_explanation(
    user_id: str,
    song: dict,
    similar_user_ids: list[str],
    user_genre_profile: dict[str, float],
) -> dict:
    """
    Build a structured explanation for a single recommendation.

    Args:
        user_id:            The session user receiving the recommendation.
        song:               Song dict with fields: genre, energy_level, tempo.
        similar_user_ids:   IDs of users with similar taste (from SVD neighbours).
        user_genre_profile: Dict of {genre: affinity_score} for this user.
                            e.g. {"Afrobeats": 0.82, "Amapiano": 0.45}

    Returns:
        Explanation dict matching the JSONB structure in the ERD:
        {
            "similar_users": [...],
            "matched_features": {
                "genre": "Afrobeats",
                "energy_level": 0.87,
                "tempo": "High"
            },
            "confidence": 0.91
        }
    """
    genre = song.get("genre", "Unknown")
    energy = song.get("energy_level", 0.5)
    tempo_bpm = song.get("tempo", 100)

    # Derive tempo label from BPM
    tempo_label = _bpm_to_label(tempo_bpm)

    # Confidence: blend genre affinity + energy match
    genre_affinity = user_genre_profile.get(genre, 0.1)
    confidence = round(min(0.99, genre_affinity * 0.7 + energy * 0.3), 2)

    explanation = {
        "similar_users": similar_user_ids[:5],  # cap at 5 for readability
        "matched_features": {
            "genre": genre,
            "energy_level": round(energy, 2),
            "tempo": tempo_label,
        },
        "confidence": confidence,
    }

    logger.debug("Built explanation for user %s → song %s", user_id, song.get("id"))
    return explanation


def _bpm_to_label(bpm: float) -> str:
    """Convert raw BPM value to a human-readable tempo label."""
    if bpm < 80:
        return "Low"
    elif bpm < 120:
        return "Medium"
    else:
        return "High"


def build_user_genre_profile(listening_events: list[dict]) -> dict[str, float]:
    """
    Derive a user's genre affinity scores from their listening history.

    Affinity is calculated as:
        (total seconds listened in genre) / (total seconds listened overall)

    Args:
        listening_events: List of event dicts with fields:
                          song_genre, play_duration_sec

    Returns:
        Dict of {genre: affinity_score} where all scores sum to ~1.0
    """
    genre_seconds: dict[str, float] = {}
    total_seconds: float = 0

    for event in listening_events:
        genre = event.get("song_genre", "Unknown")
        duration = event.get("play_duration_sec", 0)
        genre_seconds[genre] = genre_seconds.get(genre, 0) + duration
        total_seconds += duration

    if total_seconds == 0:
        return {}

    return {
        genre: round(seconds / total_seconds, 3)
        for genre, seconds in genre_seconds.items()
    }
