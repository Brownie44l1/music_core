from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Browser session identifier")
    song_id: str = Field(..., description="Song identifier")
    feedback_type: str = Field(
        ..., description="'like', 'dislike', or 'skip'",
    )


class FeedbackResponse(BaseModel):
    status: str = "ok"
    message: str = "Feedback recorded"
