from pydantic import BaseModel

from app.schemas.recommendations import Explanation


class ExplainResponse(BaseModel):
    recommendation_id: str
    song_id: str
    title: str
    artist: str
    explanation: Explanation
