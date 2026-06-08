from fastapi import APIRouter, HTTPException

from app.schemas.explain import ExplainResponse

router = APIRouter()


@router.get("/explain", response_model=ExplainResponse)
async def explain_recommendation(recommendation_id: str):
    """
    Return the explanation for a previously served recommendation.

    Reads the JSONB explanation from the Recommendation table.
    TODO (Ticket 3.4): Implement — query DB, enrich with song data.
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")
