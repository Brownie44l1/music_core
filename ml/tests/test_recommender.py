"""
Tests for the MusicRecommender and cold start logic.
Run with: uv run pytest
"""

import pandas as pd
import pytest

from app.cold_start import get_cold_start_recommendations, is_cold_start
from app.explainer import build_user_genre_profile, _bpm_to_label


# ── Cold start tests ──────────────────────────────────────────────────────────

class TestColdStart:
    def test_is_cold_start_below_threshold(self):
        assert is_cold_start(0) is True
        assert is_cold_start(4) is True

    def test_is_cold_start_at_threshold(self):
        assert is_cold_start(5) is False

    def test_is_cold_start_above_threshold(self):
        assert is_cold_start(10) is False

    def test_cold_start_returns_correct_count(self):
        songs = [
            {"id": str(i), "title": f"Song {i}", "artist": "Artist",
             "genre": genre, "popularity_score": float(i) / 10,
             "energy_level": 0.5}
            for i, genre in enumerate(
                ["Afrobeats", "Afropop", "Amapiano", "Highlife", "Fuji", "Alte",
                 "Afrobeats", "Afropop", "Amapiano", "Highlife", "Fuji", "Alte"]
            )
        ]
        result = get_cold_start_recommendations(songs, limit=10)
        assert len(result) == 10

    def test_cold_start_includes_multiple_genres(self):
        songs = [
            {"id": str(i), "title": f"Song {i}", "artist": "Artist",
             "genre": genre, "popularity_score": 0.9, "energy_level": 0.5}
            for i, genre in enumerate(
                ["Afrobeats", "Afropop", "Amapiano", "Highlife", "Fuji", "Alte",
                 "Afrobeats", "Afropop", "Amapiano", "Highlife", "Fuji", "Alte"]
            )
        ]
        result = get_cold_start_recommendations(songs, limit=6)
        genres_returned = {s["genre"] for s in result}
        assert len(genres_returned) > 1, "Cold start should return diverse genres"


# ── Explainer tests ───────────────────────────────────────────────────────────

class TestExplainer:
    def test_bpm_to_label_low(self):
        assert _bpm_to_label(60) == "Low"

    def test_bpm_to_label_medium(self):
        assert _bpm_to_label(100) == "Medium"

    def test_bpm_to_label_high(self):
        assert _bpm_to_label(140) == "High"

    def test_genre_profile_sums_to_one(self):
        events = [
            {"song_genre": "Afrobeats", "play_duration_sec": 30},
            {"song_genre": "Afrobeats", "play_duration_sec": 30},
            {"song_genre": "Amapiano", "play_duration_sec": 30},
        ]
        profile = build_user_genre_profile(events)
        assert abs(sum(profile.values()) - 1.0) < 0.01

    def test_genre_profile_empty_events(self):
        profile = build_user_genre_profile([])
        assert profile == {}

    def test_genre_profile_dominant_genre(self):
        events = [
            {"song_genre": "Afrobeats", "play_duration_sec": 90},
            {"song_genre": "Fuji", "play_duration_sec": 10},
        ]
        profile = build_user_genre_profile(events)
        assert profile["Afrobeats"] > profile["Fuji"]
