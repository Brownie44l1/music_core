import json
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from app.cache import get_cache
from app.schemas.recommendations import RecommendationResponse

logger = logging.getLogger(__name__)
router = APIRouter()

CACHE_TTL = 300  # 5 minutes


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    session_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    cache=Depends(get_cache),
) -> RecommendationResponse:
    """
    Get personalised song recommendations for a session.
    - Checks Redis cache first (TTL 5 min)
    - Falls back to ML engine if cache miss
    """
    cache_key = f"recommendations:{session_id}:{limit}"

    # ── Cache check ───────────────────────────────────────────────────
    try:
        cached = await cache.get(cache_key)
        if cached:
            logger.info("Cache hit for session %s", session_id)
            return RecommendationResponse(**json.loads(cached))
    except Exception as e:
        logger.warning("Cache read failed: %s", e)

    # ── Call ML engine ────────────────────────────────────────────────
    import os
    ml_url = os.getenv("ML_ENGINE_URL", "http://ml:8001")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ml_url}/ml/recommend",
                json={"session_id": session_id, "limit": limit},
            )
            response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ML engine timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"ML engine error: {e}")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="ML engine unavailable")

    data = response.json()

    # ── Cache the result ──────────────────────────────────────────────
    try:
        await cache.setex(cache_key, CACHE_TTL, json.dumps(data))
        logger.info("Cached recommendations for session %s", session_id)
    except Exception as e:
        logger.warning("Cache write failed: %s", e)

    return RecommendationResponse(**data)
