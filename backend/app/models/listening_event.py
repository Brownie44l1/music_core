import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ListeningEvent(Base):
    __tablename__ = "listening_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"),
    )
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id"),
    )
    play_duration_sec: Mapped[int] = mapped_column(Integer)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="listening_events")
    song = relationship("Song", back_populates="listening_events")
