from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    input_profile_id: Mapped[int] = mapped_column(
        ForeignKey("input_profiles.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    provider: Mapped[str | None] = mapped_column(String(32))
    external_task_id: Mapped[str | None] = mapped_column(String(128))
    character_task_ref: Mapped[str | None] = mapped_column(String(128))
    spirit_task_ref: Mapped[str | None] = mapped_column(String(128))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="generation_tasks")
    input_profile = relationship("InputProfile", back_populates="generation_tasks")
    model_assets = relationship("ModelAsset", back_populates="generation_task")
    evaluation_logs = relationship("EvaluationLog", back_populates="generation_task")
