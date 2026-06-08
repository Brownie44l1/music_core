import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(String)
    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("artists.id"),
    )
    genre: Mapped[str] = mapped_column(String)
    energy_level: Mapped[float] = mapped_column(Float)
    tempo: Mapped[float] = mapped_column(Float)
    popularity_score: Mapped[float] = mapped_column(Float)
    deezer_track_id: Mapped[str | None] = mapped_column(String, nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String, nullable=True)
    album_art_url: Mapped[str | None] = mapped_column(String, nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    artist = relationship("Artist", back_populates="songs")
    listening_events = relationship("ListeningEvent", back_populates="song")
    feedbacks = relationship("UserFeedback", back_populates="song")
    recommendations = relationship("Recommendation", back_populates="song")
