# music_core backend

FastAPI API layer for the music recommendation system.

## Local development

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

| Method | Path                | Description                  |
|--------|---------------------|------------------------------|
| GET    | `/health`           | Health check                 |
| GET    | `/api/recommendations` | Get song recommendations  |
| POST   | `/api/feedback`     | Submit like/dislike/skip     |
| GET    | `/api/songs`        | Browse songs by genre        |
| GET    | `/api/explain`      | Get explanation for a rec    |
