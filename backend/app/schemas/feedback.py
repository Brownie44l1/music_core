from typing import Literal
from pydantic import BaseModel, Field, field_validator


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Browser session identifier")
    song_id: str = Field(..., description="Song identifier")
    feedback_type: Literal["like", "dislike", "skip"] = Field(
        ..., description="'like', 'dislike', or 'skip'",
    )

    @field_validator("feedback_type", mode="before")
    @classmethod
    def normalize_feedback_type(cls, v: str) -> str:
        if isinstance(v, str):
            return v.lower()
        return v


class FeedbackResponse(BaseModel):
    status: str = "ok"
    message: str = "Feedback recorded"
