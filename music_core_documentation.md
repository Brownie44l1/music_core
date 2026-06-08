# music_core — Full Project Documentation

> A personalised Nigerian music recommendation system built as an academic ML project.  
> Demonstrates collaborative filtering with explainable AI, powered by a hybrid real + synthetic dataset.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Product Requirements Document (PRD)](#2-product-requirements-document-prd)
3. [Technical Requirements Document (TRD)](#3-technical-requirements-document-trd)
4. [Entity Relationship Document (ERD)](#4-entity-relationship-document-erd)
5. [Architecture](#5-architecture)
6. [Folder Structure](#6-folder-structure)
7. [Epics and Tickets](#7-epics-and-tickets)
8. [Build Order](#8-build-order)
9. [Data Strategy](#9-data-strategy)
10. [Demo Strategy](#10-demo-strategy)
11. [Known Limitations and Tradeoffs](#11-known-limitations-and-tradeoffs)

---

## 1. Project Overview

**One-liner:**
> This app recommends and streams personalised music for Nigerian users so that they discover songs they love without manually searching or curating playlists.

**Academic context:**
`music_core` is an academic ML project that demonstrates a personalised music recommendation system for Nigerian users. It is built to be explainable and presentable — not a production competitor to Spotify.

**Key differentiator:**
Most recommendation datasets are Western-skewed. `music_core` addresses this by augmenting a public dataset with a synthetically generated Nigerian music layer covering Afrobeats, Afropop, Amapiano, Highlife, Fuji, and Alte. The system also implements Explainable AI (XAI) so users and evaluators understand *why* each song was recommended.

---

## 2. Product Requirements Document (PRD)

### 2.1 What We Are Building

A web-based music recommendation system that:
- Learns Nigerian user listening preferences
- Suggests personalised songs using collaborative filtering
- Explains every recommendation in plain English
- Operates without user accounts (session-based)

### 2.2 Who It Is For

| User | Description |
|---|---|
| **Primary** | Nigerian music listener, aged 18–30, already uses Spotify or Audiomack |
| **Secondary** | Professor and presentation audience evaluating the ML system |

### 2.3 Core User Flows (Happy Path)

**Flow 1 — Onboarding (Skippable)**
```
User lands on app
→ Optionally selects favourite genres (from 6)
→ Optionally selects 5–10 seed artists
→ System builds initial taste profile
→ First recommendations generated
→ [If skipped] → System shows Nigerian Top Picks fallback
```

**Flow 2 — Recommendation and Explanation**
```
User sees list of recommended songs
→ Each song shows: title, artist, album art, confidence score
→ User clicks "Why this?" button
→ Panel shows: similar users, matched features, confidence score
→ User clicks 👍 or 👎
→ Feedback updates their profile in real time
→ Next recommendations reflect feedback
```

**Flow 3 — Exploration**
```
User browses songs by genre
→ System records listening events
→ Recommendations update after each session
```

### 2.4 Out of Scope

| Feature | Reason |
|---|---|
| Full track streaming | Licensing complexity; 30-sec previews used instead |
| User authentication | Unnecessary for academic scope |
| Social features | Out of scope |
| Mobile app | Web only |
| Payment / subscriptions | Out of scope |
| Live chart data pipeline | Static dataset used |
| Artist profile pages | Out of scope |
| Podcast or video support | Out of scope |

### 2.5 Explainability Feature

Each recommendation exposes:

| Signal | Example |
|---|---|
| Similar users | "5 users with similar taste also love this song" |
| Matched features | "Genre: Afrobeats · Energy: High · Tempo: 112 BPM" |
| Confidence score | "91% match based on your listening history" |

This is built on **Explainable AI (XAI)** principles and is the primary academic differentiator of the project.

### 2.6 Cold Start Strategy

If a user skips onboarding or has fewer than 5 listening events:
- System defaults to **Nigerian Top Picks** — most popular songs across all 6 genres
- Labelled clearly in the UI as *"Popular in Nigeria right now"*
- Personalisation activates progressively as listening data is collected

### 2.7 Known Assumptions

| Assumption | Risk |
|---|---|
| Users interact honestly with onboarding | Mitigated by making onboarding skippable |
| Professor expects a working demo | Confirmed — both demo and report required |

---

## 3. Technical Requirements Document (TRD)

### 3.1 Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **Frontend** | React.js | Component-based; ideal for dynamic recommendation cards |
| **Backend API** | FastAPI (Python) | Same language as ML code; auto-generates API docs |
| **ML Engine** | Scikit-learn + Surprise | Surprise is built specifically for collaborative filtering |
| **Database** | PostgreSQL | Relational, industry standard, handles joins cleanly |
| **Cache** | Redis | Caches precomputed recommendations; prevents demo lag |
| **Music Metadata** | Deezer API (free) | No auth required; provides preview URLs and album art |
| **Deployment** | Docker + Render.com | Free tier; live URL without localhost |

### 3.2 Deployment Architecture

| Service | Deployment Target |
|---|---|
| `frontend/` | Render.com — Static Site |
| `backend/` | Render.com — Web Service |
| `ml/` | Render.com — Web Service (higher memory) |

The `backend/` communicates with `ml/` via internal HTTP. They are deployed separately so the ML model can be retrained and redeployed independently of the API.

### 3.3 Alternative Approaches Considered

**Option B — Simplified Stack**

| Component | Choice |
|---|---|
| Frontend | Plain HTML/CSS/JS |
| Backend | Flask |
| ML | Scikit-learn only |
| Database | SQLite |
| Deploy | Localhost |

*Trade-offs: faster to build, lower risk, less impressive. SQLite struggles with large datasets. No live URL.*

**Option C — Ambitious Stack**

| Component | Choice |
|---|---|
| Frontend | React + D3.js visualisations |
| ML | Matrix factorisation from scratch (no Surprise) |
| Deploy | AWS EC2 |

*Trade-offs: highest ceiling, highest risk, 3x more development time.*

**Decision: Option A (proposed stack).** Balanced between impressiveness and buildability within academic timeline.

### 3.4 Weakest Points

| Risk | Mitigation |
|---|---|
| Redis adds operational complexity | Drop Redis if time-constrained; accept slower recs |
| Deezer API depends on live network | Pre-fetch all metadata and store locally before demo day |
| ML engine is synchronous and blocking | Acceptable at demo scale; documented as known limitation |

---

## 4. Entity Relationship Document (ERD)

### 4.1 Entities and Fields

**User**
```sql
User
─────────────────────────────────────────
id                UUID        PRIMARY KEY
session_id        VARCHAR     -- browser session identifier
onboarding_done   BOOLEAN     
created_at        TIMESTAMP
```

**Artist**
```sql
Artist
─────────────────────────────────────────
id                UUID        PRIMARY KEY
name              VARCHAR
genre             VARCHAR     -- primary genre
popularity_tier   INTEGER     -- 1 (global), 2 (regional), 3 (emerging)
origin_country    VARCHAR     -- 'NG' for Nigerian artists
deezer_artist_id  VARCHAR
created_at        TIMESTAMP
```

**Song**
```sql
Song
─────────────────────────────────────────
id                UUID        PRIMARY KEY
title             VARCHAR
artist_id         UUID        FOREIGN KEY → Artist
genre             VARCHAR
energy_level      FLOAT       -- 0.0 to 1.0 (from Deezer)
tempo             FLOAT       -- BPM
popularity_score  FLOAT       -- normalised chart position
deezer_track_id   VARCHAR
preview_url       VARCHAR     -- 30-second clip
album_art_url     VARCHAR
is_synthetic      BOOLEAN     -- TRUE for augmented Nigerian data
created_at        TIMESTAMP
```

**ListeningEvent**
```sql
ListeningEvent
─────────────────────────────────────────
id                UUID        PRIMARY KEY
user_id           UUID        FOREIGN KEY → User
song_id           UUID        FOREIGN KEY → Song
play_duration_sec INTEGER     -- implicit signal
completed         BOOLEAN     -- did user hear full preview?
source            VARCHAR     -- 'recommendation' | 'browse' | 'onboarding'
created_at        TIMESTAMP
```

**UserFeedback**
```sql
UserFeedback
─────────────────────────────────────────
id                UUID        PRIMARY KEY
user_id           UUID        FOREIGN KEY → User
song_id           UUID        FOREIGN KEY → Song
feedback_type     VARCHAR     -- 'like' | 'dislike' | 'skip'
created_at        TIMESTAMP
```

**Recommendation**
```sql
Recommendation
─────────────────────────────────────────
id                UUID        PRIMARY KEY
user_id           UUID        FOREIGN KEY → User
song_id           UUID        FOREIGN KEY → Song
score             FLOAT       -- model confidence 0.0–1.0
explanation       JSONB       -- see structure below
algorithm_version VARCHAR     -- tracks which model version generated this
served_at         TIMESTAMP
interacted        BOOLEAN     -- did user click this recommendation?
```

**Explanation JSONB Structure**
```json
{
  "similar_users": ["uuid-1", "uuid-2", "uuid-3"],
  "matched_features": {
    "genre": "Afrobeats",
    "energy_level": 0.87,
    "tempo": "High"
  },
  "confidence": 0.91
}
```

### 4.2 Relationships

```
User          1 ──── M    ListeningEvent
User          1 ──── M    UserFeedback
User          1 ──── M    Recommendation
Song          1 ──── M    ListeningEvent
Song          1 ──── M    UserFeedback
Song          1 ──── M    Recommendation
Artist        1 ──── M    Song
```

### 4.3 Known Design Decisions and Tradeoffs

| Decision | Tradeoff |
|---|---|
| `genre` exists on both `Artist` and `Song` | An artist may make cross-genre songs. A proper solution is a separate Genre table with many-to-many. Accepted for scope. |
| No authentication — session-based only | Clearing browser cookies or opening incognito loses listening history. Accepted tradeoff. In production, optional account creation would fix this. |
| `is_synthetic` flag on Song | Enables transparent separation of real vs augmented data during presentation. |

---

## 5. Architecture

### 5.1 System Diagram

```
                     ┌─────────────────────┐
                     │       BROWSER        │
                     │                     │
                     │   React.js Frontend │
                     │                     │
                     │  - Song cards       │
                     │  - 👍 👎 feedback   │
                     │  - "Why?" panel     │
                     │  - Genre browser    │
                     └────────┬────────────┘
                              │
                     HTTP REST│API
                              │
                     ┌────────▼────────────┐
                     │                     │
                     │   FastAPI Backend   │
                     │                     │
                     │  /recommendations   │
                     │  /feedback          │
                     │  /songs             │
                     │  /explain           │
                     └──┬──────────┬───────┘
                        │          │
            ┌───────────▼──┐  ┌────▼─────────────┐
            │              │  │                  │
            │  PostgreSQL  │  │      Redis       │
            │              │  │                  │
            │  - Users     │  │  Cached recs     │
            │  - Songs     │  │  per session_id  │
            │  - Artists   │  │                  │
            │  - Events    │  └──────────────────┘
            │  - Recs      │
            └──────┬───────┘
                   │
       ┌───────────▼───────────┐
       │                       │
       │      ML Engine        │
       │      (Python)         │
       │                       │
       │  1. Collaborative     │
       │     Filtering         │
       │     (Surprise lib)    │
       │                       │
       │  2. Explainability    │
       │     Generator         │
       │                       │
       │  3. Cold Start        │
       │     Fallback          │
       │                       │
       └───────────┬───────────┘
                   │
       ┌───────────▼───────────┐
       │                       │
       │      Deezer API       │
       │      (External)       │
       │                       │
       │  - Preview URLs       │
       │  - Album art          │
       │  - Track metadata     │
       │                       │
       └───────────────────────┘
```

### 5.2 End-to-End Request Flow

```
1. Browser sends:
   GET /recommendations?session_id=abc123

2. FastAPI receives request
   → Checks Redis: "Do I have cached recs for abc123?"

3a. Cache HIT
   → Return recommendations immediately ⚡

3b. Cache MISS
   → Query PostgreSQL for ListeningEvents + Feedback
   → Pass interaction matrix to ML Engine
   → ML Engine runs Collaborative Filtering
   → Generates top 10 songs + explanations
   → Stores results in PostgreSQL (Recommendation table)
   → Caches results in Redis (expires: 1 hour)
   → Returns recommendations to browser

4. Browser renders song cards with confidence scores

5. User clicks "Why this song?"
   → GET /explain?recommendation_id=xyz
   → FastAPI reads explanation JSONB from PostgreSQL
   → Joins Song table to enrich feature data
   → Returns: genre match, similar users, confidence
   → Frontend renders explanation panel

6. User clicks 👍 or 👎
   → POST /feedback {song_id, feedback_type}
   → FastAPI writes to UserFeedback table
   → Redis cache invalidated for this session
   → Next request triggers fresh recommendations
```

### 5.3 Failure Points and Scale Considerations

**Most likely demo failure point:** Deezer API (external network dependency)
**Mitigation:** Pre-fetch all metadata before demo day. Never call Deezer live during the presentation.

**What changes at 100k users:**

| Current (Academic) | Production (100k users) |
|---|---|
| Single FastAPI server | Load balancer + multiple API servers |
| Single PostgreSQL | PostgreSQL with read replicas |
| Redis single instance | Redis cluster |
| ML runs per request | Nightly batch recomputation + async job queue |
| Deezer free API | Music licensing + self-hosted audio CDN |
| Single Docker container | Kubernetes orchestration |

---

## 6. Folder Structure

```
music_core/
├── frontend/                   → React.js app
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SongCard/
│   │   │   ├── ExplainPanel/
│   │   │   ├── GenreBrowser/
│   │   │   └── InsightsDashboard/
│   │   ├── pages/
│   │   │   ├── Onboarding.jsx
│   │   │   ├── Home.jsx
│   │   │   └── Browse.jsx
│   │   ├── hooks/
│   │   ├── services/           → API call functions
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
│
├── backend/                    → FastAPI app
│   ├── app/
│   │   ├── routers/
│   │   │   ├── recommendations.py
│   │   │   ├── feedback.py
│   │   │   ├── songs.py
│   │   │   └── explain.py
│   │   ├── models/             → SQLAlchemy DB models
│   │   ├── schemas/            → Pydantic schemas
│   │   ├── db.py               → PostgreSQL connection
│   │   ├── cache.py            → Redis connection
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml/                         → ML Engine
│   ├── app/
│   │   ├── recommender.py      → Collaborative filtering (Surprise)
│   │   ├── explainer.py        → Explanation generator
│   │   ├── cold_start.py       → Fallback logic
│   │   └── main.py             → FastAPI endpoint for ML service
│   ├── models/                 → Saved trained model files
│   ├── notebooks/              → Jupyter exploration notebooks
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_synthetic_generation.ipynb
│   │   ├── 03_model_training.ipynb
│   │   └── 04_model_evaluation.ipynb
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/
│   ├── raw/                    → Original Last.fm dataset (unmodified)
│   ├── processed/              → Cleaned and merged dataset
│   ├── synthetic/              → Generated Nigerian listening data
│   └── seeds/                  → Nigerian artists + songs CSV/JSON
│       ├── nigerian_artists.csv
│       └── nigerian_songs.csv
│
├── docker-compose.yml          → Runs all services locally
└── README.md
```

---

## 7. Epics and Tickets

### Epic 1 — Data Foundation
*Goal: Clean, combined dataset ready to feed the ML engine*

---

**Ticket 1.1 — Acquire and explore the Last.fm dataset**

```
Task:
  Download the Last.fm 360K or HetRec Last.fm dataset.
  Explore in a Jupyter notebook.
  Document: user count, song count, interaction count,
  matrix sparsity.

Acceptance Criteria:
  ✅ Dataset downloaded and loadable in Python
  ✅ Notebook shows basic stats (user count, song count,
     interaction count, sparsity of the matrix)
  ✅ You can explain what "matrix sparsity" means
     and why it matters for collaborative filtering
```

---

**Ticket 1.2 — Build the Nigerian artist and song dataset**

```
Task:
  Using the 3-layer selection framework, compile
  30–40 Nigerian artists across 6 genres and
  3 popularity tiers. Source from Nigeria charts
  on Spotify, Audiomack, Apple Music.
  Store as structured CSV.

Acceptance Criteria:
  ✅ At least 5 artists per genre
  ✅ At least 3 artists per popularity tier
  ✅ Each artist has: name, genre, tier,
     origin_country, deezer_artist_id
  ✅ Chart sources documented (platform + date)
```

---

**Ticket 1.3 — Fetch song metadata from Deezer API**

```
Task:
  For each Nigerian artist, query Deezer API
  and fetch top 5 songs. Store all metadata locally.
  Do NOT rely on live API calls after this point.

Acceptance Criteria:
  ✅ All ~200 songs stored in PostgreSQL songs table
  ✅ Every song has a verified working preview_url
  ✅ is_synthetic flag correctly set on all records
  ✅ Script is rerunnable without breaking anything
```

---

**Ticket 1.4 — Generate synthetic listening behaviour**

```
Task:
  Write a Python script that generates synthetic
  user-song interaction data for Nigerian artists,
  based on statistical patterns from Last.fm.
  Generate at least 500 synthetic users with
  realistic listening distributions.

Acceptance Criteria:
  ✅ Synthetic interactions follow power-law distribution
  ✅ is_synthetic flag propagated to interactions
  ✅ Data loadable into PostgreSQL
  ✅ You can explain why power-law distribution
     was chosen
```

---

**Ticket 1.5 — Merge and validate the combined dataset**

```
Task:
  Combine Last.fm data and synthetic Nigerian data
  into one unified interaction matrix.
  Run validation checks. Split into train/test sets.

Acceptance Criteria:
  ✅ No duplicate song IDs across datasets
  ✅ No users with zero interactions
  ✅ Matrix sparsity documented
  ✅ Data split into train/test sets for evaluation
```

---

### Epic 2 — ML Engine
*Goal: Working collaborative filtering model with explainability*

---

**Ticket 2.1 — Build baseline collaborative filtering model**

```
Task:
  Using the Surprise library, implement SVD-based
  collaborative filtering. Train on training set,
  evaluate on test set.

Acceptance Criteria:
  ✅ Model trains without errors
  ✅ Evaluation metrics computed: RMSE, Precision@10,
     Recall@10
  ✅ You can explain Precision@10 in plain English
  ✅ Results logged in a notebook
```

---

**Ticket 2.2 — Implement cold start fallback**

```
Task:
  For users with fewer than 5 listening events,
  return popularity-based fallback showing top songs
  across all 6 Nigerian genres.

Acceptance Criteria:
  ✅ System detects when user has <5 interactions
  ✅ Fallback returns at least 10 songs
  ✅ Songs are diverse across all 6 genres
  ✅ UI labels fallback as "Popular in Nigeria right now"
```

---

**Ticket 2.3 — Build explainability generator**

```
Task:
  For each recommendation, generate a structured
  explanation object showing similar users,
  matched features, and confidence score.

Acceptance Criteria:
  ✅ Explanation generated for every recommendation
  ✅ Stored as JSONB in Recommendation table
  ✅ References at least 2 similar users
     and at least 2 matched features
  ✅ Confidence score between 0.0 and 1.0
```

---

**Ticket 2.4 — Model evaluation and algorithm comparison**

```
Task:
  Compare at least 2 algorithms from Surprise
  (e.g. SVD vs KNNBasic). Document results.
  Choose final algorithm with written justification.

Acceptance Criteria:
  ✅ Both algorithms tested on same dataset
  ✅ Metrics compared in a clean table
  ✅ Final algorithm choice justified in writing
  ✅ Justification included in presentation
```

---

### Epic 3 — Backend API
*Goal: FastAPI server exposing all ML functionality*

---

**Ticket 3.1 — Project setup and database schema**

```
Task:
  Set up FastAPI project. Create PostgreSQL schema
  matching the ERD. Set up Docker Compose with
  FastAPI + PostgreSQL + Redis running together.

Acceptance Criteria:
  ✅ docker-compose up starts all 3 services cleanly
  ✅ All 6 tables created with correct fields
  ✅ Database seeded with song and artist data
  ✅ GET /health returns 200 OK
```

---

**Ticket 3.2 — Recommendations endpoint**

```
Task:
  Build GET /recommendations?session_id={id}
  Returns top 10 personalised songs.
  Checks Redis cache first. Falls back to ML engine.

Acceptance Criteria:
  ✅ Returns 10 recommendations in <3 seconds
  ✅ Cache hit returns in <200ms
  ✅ Cold start users receive fallback recommendations
  ✅ Response includes confidence score per song
```

---

**Ticket 3.3 — Feedback endpoint**

```
Task:
  Build POST /feedback
  Accepts: session_id, song_id, feedback_type
  Writes to UserFeedback. Invalidates Redis cache.

Acceptance Criteria:
  ✅ Feedback saved correctly to database
  ✅ Redis cache invalidated on feedback submission
  ✅ Next recommendation request reflects feedback
  ✅ Invalid feedback_type returns 400 error
```

---

**Ticket 3.4 — Explainability endpoint**

```
Task:
  Build GET /explain?recommendation_id={id}
  Returns full explanation object for a recommendation.

Acceptance Criteria:
  ✅ Returns explanation JSONB from database
  ✅ Joins Song table to enrich feature data
  ✅ Returns 404 if recommendation not found
  ✅ Response time <500ms
```

---

### Epic 4 — Frontend
*Goal: Clean React UI that makes the ML visible and interactive*

---

**Ticket 4.1 — App shell and routing**

```
Task:
  Set up React app with 3 routes:
  / (onboarding), /home (recommendations),
  /browse (genre explorer).
  Session ID generated and stored on first visit.

Acceptance Criteria:
  ✅ Session ID persisted in localStorage
  ✅ Skippable onboarding routes correctly to /home
  ✅ Basic layout renders on mobile and desktop
```

---

**Ticket 4.2 — Recommendation cards UI**

```
Task:
  Build song recommendation card component.
  Shows: album art, title, artist, genre,
  confidence score, 👍 👎 buttons, "Why this?" button.

Acceptance Criteria:
  ✅ Cards render real Deezer album art
  ✅ 30-second preview plays on click
  ✅ Feedback buttons call /feedback endpoint
  ✅ Loading state shown while fetching recommendations
```

---

**Ticket 4.3 — Explainability panel**

```
Task:
  Build the "Why was this recommended?" drawer.
  Shows similar users, matched features,
  and confidence score.

Acceptance Criteria:
  ✅ Opens on "Why this?" click
  ✅ Shows: genre match, energy match,
     confidence score as a visual bar
  ✅ Uses plain English — no ML jargon visible
  ✅ Closes cleanly without breaking the UI
```

---

**Ticket 4.4 — Genre browser**

```
Task:
  Build browse page where users explore songs
  by genre. Listening events recorded on play.

Acceptance Criteria:
  ✅ All 6 genres displayed
  ✅ At least 5 songs visible per genre
  ✅ Listening events recorded when song plays
  ✅ Links back to recommendation feed
```

---

### Epic 5 — Explainability Feature
*Your academic differentiator*

---

**Ticket 5.1 — Confidence score visualisation**

```
Task:
  Add visual confidence meter to each
  recommendation card.

Acceptance Criteria:
  ✅ Visual progress bar or circular meter
  ✅ Colour coded:
     green  >70%
     yellow  40–70%
     red    <40%
  ✅ Tooltip explains what the score means
```

---

**Ticket 5.2 — Model transparency dashboard**

```
Task:
  Build /insights page showing:
  user's top genres, listening pattern,
  how recommendations shifted after feedback.

Acceptance Criteria:
  ✅ Shows user's top 3 genres by play count
  ✅ Shows how recommendations shifted after feedback
  ✅ All data pulled from real database queries
  ✅ Designed to be screenshottable for report
```

---

### Epic 6 — Demo Preparation
*Never skip this epic*

---

**Ticket 6.1 — Seed demo users**

```
Task:
  Create 3 demo user profiles with pre-computed,
  cached recommendations.

Demo Users:
  User 1 — "The Afrobeats Purist"
    Heavy: Burna Boy, Wizkid, Davido
    Expected recs: Afropop, some Amapiano

  User 2 — "The Explorer"
    Mixed: Highlife + Alte + Amapiano
    Expected recs: cross-genre surprises

  User 3 — "The New User" (cold start)
    No history
    Expected recs: Nigerian Top Picks fallback

Acceptance Criteria:
  ✅ 3 demo session IDs documented
  ✅ Recommendations pre-cached in Redis
  ✅ Each user produces meaningfully different recs
     (verified manually)
```

---

**Ticket 6.2 — Deploy to Render.com**

```
Task:
  Deploy full stack to Render.com.
  Verify all endpoints work on live URL.

Acceptance Criteria:
  ✅ Live URL accessible without localhost
  ✅ All 3 demo users work on live deployment
  ✅ Deezer previews play on live deployment
  ✅ Tested on mobile
```

---

## 8. Build Order

Build in phases so something is always demoable.

```
PHASE 1 — Walking Skeleton (Days 1–3)
  Ticket 3.1  Docker + DB setup
  Ticket 4.1  App shell and routing
  Ticket 4.2  Cards UI with hardcoded/fake data
  ─────────────────────────────────────────────
  Goal: Something renders in a browser

PHASE 2 — Real Data (Days 4–7)
  Ticket 1.1  Last.fm dataset acquisition
  Ticket 1.2  Nigerian artists dataset
  Ticket 1.3  Deezer metadata fetch + local storage
  ─────────────────────────────────────────────
  Goal: Real songs appear in the UI

PHASE 3 — ML Engine (Days 8–12)
  Ticket 1.4  Synthetic data generation
  Ticket 1.5  Merge and validate dataset
  Ticket 2.1  Baseline CF model
  Ticket 2.2  Cold start fallback
  Ticket 3.2  Recommendations endpoint
  Ticket 3.3  Feedback endpoint
  ─────────────────────────────────────────────
  Goal: Real personalised recommendations working

PHASE 4 — Explainability (Days 13–16)
  Ticket 2.3  Explanation generator
  Ticket 3.4  Explain endpoint
  Ticket 4.3  Explanation panel UI
  Ticket 5.1  Confidence score visualisation
  Ticket 5.2  Model transparency dashboard
  ─────────────────────────────────────────────
  Goal: The demo centrepiece is working

PHASE 5 — Polish and Ship (Days 17–21)
  Ticket 2.4  Model evaluation and comparison
  Ticket 4.4  Genre browser
  Ticket 6.1  Seed demo users
  Ticket 6.2  Deploy to Render.com
  ─────────────────────────────────────────────
  Goal: Live URL, demo-ready, presentation-ready
```

---

## 9. Data Strategy

### 9.1 Approach: Hybrid Real + Synthetic

| Layer | Source | Purpose |
|---|---|---|
| **Real** | Last.fm 360K or HetRec dataset | Realistic user-song interaction patterns |
| **Synthetic** | Generated from Last.fm patterns | Nigerian/Afrobeats artist coverage |

This mirrors a real-world data engineering challenge and is presentable as **data augmentation** — a legitimate ML technique.

### 9.2 Nigerian Artist Selection Framework

**Layer 1 — Genre Coverage**

| Genre | Character |
|---|---|
| Afrobeats | Mainstream, danceable, global crossover |
| Afropop | Melody-driven, radio-friendly |
| Amapiano | South African origin, dominant in Nigeria |
| Highlife | Guitar-driven, Eastern Nigeria roots |
| Fuji | Islamic/Yoruba, percussion-heavy |
| Alte | Indie, experimental, younger audience |

**Layer 2 — Popularity Tiers**

| Tier | Range | Examples |
|---|---|---|
| 1 — Global | 10M+ monthly Spotify listeners | Burna Boy, Wizkid, Davido, Tems, Ayra Starr |
| 2 — Regional | 1M–10M monthly listeners | Asake, Kizz Daniel, Fireboy DML, Omah Lay |
| 3 — Emerging | Under 1M | Shallipopi, Odumodublvck, Lojay |

**Layer 3 — Validation Sources**
- Spotify Charts Nigeria
- Apple Music Nigeria Top 100
- Audiomack Nigeria Charts
- Turntable Charts Nigeria

*Selection window: 3–6 months of chart data*

**Target dataset size:**
```
~30–40 artists
~150–200 songs (4–6 songs per artist)
6 genres
3 popularity tiers
```

### 9.3 Presentable Data Statement

> *"Public datasets underrepresent African music, so we augmented with synthetic Nigerian listening data generated from real behavioural patterns found in the Last.fm dataset. Artist selection was driven by Nigerian chart data from Spotify, Apple Music, and Audiomack over a 6-month period, stratified by genre and popularity tier."*

---

## 10. Demo Strategy

### 10.1 Pre-Demo Checklist

```
□ All Deezer metadata pre-fetched and stored locally
□ No live Deezer API calls during presentation
□ 3 demo users seeded and recommendations cached
□ Live Render.com URL tested end-to-end
□ Tested on mobile device
□ Phone hotspot ready as WiFi backup
□ Screenshots taken as last-resort fallback
```

### 10.2 Demo User Profiles

| User | Listening Profile | What to Show |
|---|---|---|
| The Afrobeats Purist | Heavy Burna Boy, Wizkid, Davido | Strong genre-consistent recommendations |
| The Explorer | Mixed Highlife + Alte + Amapiano | Cross-genre discovery recommendations |
| The New User | No history | Cold start fallback → Nigerian Top Picks |

### 10.3 Demo Script Outline

```
1. Open app as "New User"
   → Show cold start fallback
   → Explain: "No history yet — system defaults to popular Nigerian tracks"

2. Switch to "Afrobeats Purist"
   → Show personalised recommendations
   → Click "Why this?" on a song
   → Walk through explainability panel

3. Click 👎 on a recommendation
   → Show recommendations refresh
   → Explain: "Explicit feedback immediately updates the model"

4. Switch to "The Explorer"
   → Show cross-genre recommendations
   → Open /insights dashboard
   → Show how listening history shaped the profile
```

---

## 11. Known Limitations and Tradeoffs

| Limitation | Decision | Production Fix |
|---|---|---|
| No authentication | Session-based only; clearing cookies loses history | Optional account creation |
| No full track streaming | 30-second previews only | Music licensing agreements |
| Synchronous ML engine | Blocks on cache miss; acceptable at demo scale | Async job queue (Celery) |
| Genre on Artist and Song tables | Design smell; cross-genre songs may be mislabelled | Separate Genre table with many-to-many |
| Western-skewed base dataset | Mitigated by synthetic Nigerian augmentation layer | Collect real Nigerian user data |
| Single Deezer API dependency | Pre-fetch all metadata before demo day | Self-hosted metadata store |

---

*Document generated during Phase 1 engineering planning.*  
*Project: `music_core` · Stack: React + FastAPI + PostgreSQL + Redis + Deezer API · Deploy: Render.com*
