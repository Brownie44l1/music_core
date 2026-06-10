"""
Seed script — loads nigerian_artists.csv and nigerian_songs.csv into PostgreSQL.

Run from inside the backend container:
    docker compose exec backend python seed.py

Or from the host (with deps installed):
    python seed.py

Safe to re-run: upserts on natural IDs, no duplicates.
"""

import csv
import os
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/music_core",
)

# CSVs are co-located with this script inside the backend container (/app/)
SCRIPT_DIR = Path(__file__).parent
ARTISTS_CSV = SCRIPT_DIR / "nigerian_artists.csv"
SONGS_CSV = SCRIPT_DIR / "nigerian_songs.csv"


def run():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # ── Seed artists ──────────────────────────────────────────────
        print(f"Reading artists from {ARTISTS_CSV}")
        artist_rows = []
        with open(ARTISTS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                artist_rows.append(row)

        print(f"  Upserting {len(artist_rows)} artists...")
        for row in artist_rows:
            session.execute(
                text("""
                    INSERT INTO artists (id, name, genre, popularity_tier, origin_country, deezer_artist_id, created_at)
                    VALUES (:id, :name, :genre, :tier, :country, :deezer_artist_id, NOW())
                    ON CONFLICT (id) DO UPDATE
                        SET name              = EXCLUDED.name,
                            genre             = EXCLUDED.genre,
                            popularity_tier   = EXCLUDED.popularity_tier,
                            origin_country    = EXCLUDED.origin_country,
                            deezer_artist_id  = EXCLUDED.deezer_artist_id
                """),
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, row["artist_id"])),
                    "name": row["name"],
                    "genre": row["genre"],
                    "tier": int(row["tier"]),
                    "country": row["country"],
                    "deezer_artist_id": row["artist_id"],
                },
            )

        session.commit()
        print("  ✅ Artists done")

        # ── Seed songs ────────────────────────────────────────────────
        print(f"Reading songs from {SONGS_CSV}")
        song_rows = []
        with open(SONGS_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                song_rows.append(row)

        print(f"  Upserting {len(song_rows)} songs...")
        skipped = 0
        for row in song_rows:
            artist_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, row["artist_id"]))

            # Verify the artist exists before inserting
            result = session.execute(
                text("SELECT id FROM artists WHERE id = :id"),
                {"id": artist_uuid},
            ).fetchone()

            if not result:
                print(f"  ⚠️  Skipping song '{row['title']}' — artist '{row['artist_id']}' not found")
                skipped += 1
                continue

            session.execute(
                text("""
                    INSERT INTO songs (
                        id, title, artist_id, genre, energy_level, tempo,
                        popularity_score, deezer_track_id, preview_url,
                        album_art_url, is_synthetic, created_at
                    )
                    VALUES (
                        :id, :title, :artist_id, :genre, :energy_level, :tempo,
                        :popularity_score, :deezer_track_id, :preview_url,
                        :album_art_url, :is_synthetic, NOW()
                    )
                    ON CONFLICT (id) DO UPDATE
                        SET title            = EXCLUDED.title,
                            genre            = EXCLUDED.genre,
                            popularity_score = EXCLUDED.popularity_score,
                            deezer_track_id  = EXCLUDED.deezer_track_id,
                            preview_url      = EXCLUDED.preview_url,
                            is_synthetic     = EXCLUDED.is_synthetic
                """),
                {
                    "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, row["song_id"])),
                    "title": row["title"],
                    "artist_id": artist_uuid,
                    "genre": row["genre"],
                    # CSVs don't have energy/tempo columns — use rank as a
                    # normalised proxy until Deezer metadata is fetched (ticket 1.3)
                    "energy_level": 0.5,
                    "tempo": 120.0,
                    "popularity_score": round(1.0 - (int(row["rank"]) / 1_000_000), 4),
                    "deezer_track_id": row["deezer_id"],
                    "preview_url": row["preview_url"] or None,
                    "album_art_url": None,
                    "is_synthetic": False,
                },
            )

        session.commit()
        total = len(song_rows) - skipped
        print(f"  ✅ Songs done — {total} inserted/updated, {skipped} skipped")

    print("\n🎵 Seed complete.")
    print("   Test with:")
    print('   curl -X POST "http://localhost:8000/api/feedback" \\')
    print('     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"session_id": "test_user_001", "song_id": "ng_4015341011", "feedback_type": "like"}}\'')


if __name__ == "__main__":
    run()
