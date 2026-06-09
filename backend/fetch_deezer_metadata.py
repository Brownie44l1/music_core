"""
Ticket 1.3 — Deezer Metadata Fetch
────────────────────────────────────
Fetches energy_level, tempo (BPM), and album_art_url for every song
in the DB using the public Deezer track API (no auth required).

Run from inside the backend container:
    docker compose exec backend python fetch_deezer_metadata.py

Or from the host:
    python fetch_deezer_metadata.py
"""

import os
import time
import httpx
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/music_core",
)

DEEZER_API = "https://api.deezer.com/track/{track_id}"
RATE_LIMIT_DELAY = 0.25  # 250ms between requests — well within public limits


def fetch_track(client: httpx.Client, deezer_track_id: str) -> dict | None:
    try:
        r = client.get(
            DEEZER_API.format(track_id=deezer_track_id),
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()

        if "error" in data:
            print(f"  ⚠️  Deezer error for {deezer_track_id}: {data['error']}")
            return None

        # BPM → normalise to 0–1 (typical range 60–200 BPM)
        bpm = data.get("bpm", 0) or 0
        energy_level = round(min(1.0, max(0.0, (bpm - 60) / 140)), 3) if bpm else 0.5

        # Album art — prefer xl
        album_art = None
        album = data.get("album", {})
        for size in ("cover_xl", "cover_big", "cover_medium", "cover"):
            if album.get(size):
                album_art = album[size]
                break

        return {
            "tempo": float(bpm) if bpm else 120.0,
            "energy_level": energy_level,
            "album_art_url": album_art,
        }

    except httpx.HTTPError as e:
        print(f"  ❌ HTTP error for {deezer_track_id}: {e}")
        return None


def run():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        songs = conn.execute(
            text("SELECT id, deezer_track_id FROM songs WHERE deezer_track_id IS NOT NULL AND album_art_url IS NULL ORDER BY created_at")
        ).fetchall()

    print(f"Fetching metadata for {len(songs)} songs...")
    updated = 0
    skipped = 0

    with httpx.Client() as client, engine.connect() as conn:
        for i, (song_id, deezer_track_id) in enumerate(songs):
            print(f"  [{i+1}/{len(songs)}] track {deezer_track_id}...", end=" ")

            metadata = fetch_track(client, deezer_track_id)

            if not metadata:
                print("skipped")
                skipped += 1
                continue

            conn.execute(
                text("""
                    UPDATE songs
                    SET energy_level  = :energy_level,
                        tempo         = :tempo,
                        album_art_url = :album_art_url
                    WHERE id = :id
                """),
                {"id": str(song_id), **metadata},
            )
            conn.commit()

            print(f"BPM={metadata['tempo']:.0f} energy={metadata['energy_level']} art={'✓' if metadata['album_art_url'] else '✗'}")
            updated += 1

            time.sleep(RATE_LIMIT_DELAY)

    print(f"\n✅ Done — {updated} updated, {skipped} skipped")


if __name__ == "__main__":
    run()
