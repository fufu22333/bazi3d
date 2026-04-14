from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    primary_asset_id: Mapped[int] = mapped_column(
        ForeignKey("model_assets.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(16), default="private", nullable=False)
    allow_remix: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="works")
    primary_asset = relationship("ModelAsset", back_populates="works")
    favorites = relationship("Favorite", back_populates="work")
    evaluation_logs = relationship("EvaluationLog", back_populates="work")
