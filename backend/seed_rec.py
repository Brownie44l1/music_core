"""
Temporary test helper — inserts one Recommendation row so /explain can be tested.
Delete this file after ticket 3.4 is verified.
"""
import os, uuid
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/plugd")
engine = create_engine(DATABASE_URL)

SONG_DEEZER_ID = "4015341011"  # Burna Boy — Dai Dai

with engine.connect() as conn:
    # Get or create a test user
    user = conn.execute(
        text("SELECT id FROM users WHERE session_id = 'test_user_001'")
    ).fetchone()
    if not user:
        user_id = uuid.uuid4()
        conn.execute(text(
            "INSERT INTO users (id, session_id, onboarding_done, created_at) "
            "VALUES (:id, 'test_user_001', false, NOW())"
        ), {"id": str(user_id)})
    else:
        user_id = user[0]

    # Get the song
    song = conn.execute(
        text("SELECT id FROM songs WHERE deezer_track_id = :did"),
        {"did": SONG_DEEZER_ID}
    ).fetchone()
    if not song:
        print("❌ Song not found — run seed.py first")
        exit(1)
    song_id = song[0]

    # Insert a recommendation
    rec_id = uuid.uuid4()
    conn.execute(text("""
        INSERT INTO recommendations (id, user_id, song_id, score, explanation, algorithm_version, served_at, interacted)
        VALUES (:id, :user_id, :song_id, :score, CAST(:explanation AS jsonb), :algo, NOW(), false)
    """), {
        "id": str(rec_id),
        "user_id": str(user_id),
        "song_id": str(song_id),
        "score": 0.91,
        "explanation": '{"similar_users": ["uuid-1", "uuid-2", "uuid-3"], "matched_features": {"genre": "Afrobeats", "energy_level": 0.87, "tempo": "112 BPM"}, "confidence": 0.91}',
        "algo": "svd-v1",
    })
    conn.commit()

print(f"✅ Recommendation inserted: {rec_id}")
print(f"\nTest with:")
print(f'   curl "http://localhost:8000/api/explain?recommendation_id={rec_id}"')
