from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class ModelAsset(Base):
    __tablename__ = "model_assets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    generation_task_id: Mapped[int] = mapped_column(
        ForeignKey("generation_tasks.id"), nullable=False
    )
    asset_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_format: Mapped[str] = mapped_column(String(16), nullable=False)
    asset_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    generation_task = relationship("GenerationTask", back_populates="model_assets")
    works = relationship("Work", back_populates="primary_asset")
