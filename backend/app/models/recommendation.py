import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"),
    )
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id"),
    )
    score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[dict] = mapped_column(JSONB)
    algorithm_version: Mapped[str] = mapped_column(String)
    served_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    interacted: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="recommendations")
    song = relationship("Song", back_populates="recommendations")
