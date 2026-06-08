"""
Recommendation Router
──────────────────────
Exposes the ML engine's recommendation functionality via HTTP.
Called internally by the backend service — not directly by the frontend.

Endpoints:
  POST /ml/recommend   → generate recommendations for a session
"""

from fastapi import APIRouter, HTTPException

from app.cold_start import get_cold_start_recommendations, is_cold_start
from app.models.schemas import RecommendationRequest, RecommendationResponse
from app.services.model_service import ModelService

router = APIRouter()
model_service = ModelService()


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Generate personalised song recommendations for a user session.

    - If user has sufficient history: SVD collaborative filtering
    - If user is cold start (<5 interactions): popularity fallback
    """
    try:
        result = await model_service.recommend(
            session_id=request.session_id,
            limit=request.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
