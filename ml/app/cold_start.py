"""
Cold Start Fallback
───────────────────
When a user has fewer interactions than COLD_START_THRESHOLD,
we cannot generate meaningful personalised recommendations.

Strategy: return the most popular songs across all 6 Nigerian
genres, ensuring genre diversity in the fallback list.

This is labelled in the UI as "Popular in Nigeria right now"
so users understand they are seeing general recommendations,
not personalised ones.
"""

import os
from collections import defaultdict

# Loaded from the database in production — hardcoded here as scaffold
GENRES = ["Afrobeats", "Afropop", "Amapiano", "Highlife", "Fuji", "Alte"]

COLD_START_THRESHOLD = int(os.getenv("COLD_START_THRESHOLD", "5"))


def is_cold_start(interaction_count: int) -> bool:
    """Return True if the user does not have enough history for personalisation."""
    return interaction_count < COLD_START_THRESHOLD


def get_cold_start_recommendations(
    songs: list[dict],
    limit: int = 10,
) -> list[dict]:
    """
    Return the most popular songs distributed across all genres.

    Args:
        songs: List of song dicts from the database, each with a
               'genre' and 'popularity_score' field.
        limit: Total number of songs to return.

    Returns:
        List of songs evenly distributed across genres,
        sorted by popularity within each genre.
    """
    # Group songs by genre
    by_genre: dict[str, list[dict]] = defaultdict(list)
    for song in songs:
        genre = song.get("genre", "Unknown")
        by_genre[genre].append(song)

    # Sort each genre bucket by popularity descending
    for genre in by_genre:
        by_genre[genre].sort(key=lambda s: s.get("popularity_score", 0), reverse=True)

    # Round-robin across genres to ensure diversity
    results: list[dict] = []
    per_genre = max(1, limit // len(GENRES))

    for genre in GENRES:
        top_in_genre = by_genre.get(genre, [])[:per_genre]
        results.extend(top_in_genre)

    # If we're short (some genres had fewer songs), fill from remaining
    if len(results) < limit:
        seen_ids = {s["id"] for s in results}
        for song in songs:
            if song["id"] not in seen_ids:
                results.append(song)
                seen_ids.add(song["id"])
            if len(results) >= limit:
                break

    return results[:limit]
