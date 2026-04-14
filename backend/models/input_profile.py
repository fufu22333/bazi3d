from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class InputProfile(Base):
    __tablename__ = "input_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(64))
    gender: Mapped[str | None] = mapped_column(String(32))
    birth_datetime: Mapped[datetime | None] = mapped_column(DateTime)
    calendar_type: Mapped[str | None] = mapped_column(String(16))
    birth_location: Mapped[str | None] = mapped_column(String(255))
    style_profile: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    extra_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    reference_image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="input_profiles")
    generation_tasks = relationship("GenerationTask", back_populates="input_profile")
