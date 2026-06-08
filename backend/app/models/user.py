import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    onboarding_done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    listening_events = relationship("ListeningEvent", back_populates="user")
    feedbacks = relationship("UserFeedback", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
