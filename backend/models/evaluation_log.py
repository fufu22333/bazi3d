from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    generation_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("generation_tasks.id")
    )
    work_id: Mapped[int | None] = mapped_column(ForeignKey("works.id"))
    level: Mapped[str] = mapped_column(String(32), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    subjective_score: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    generation_task = relationship("GenerationTask", back_populates="evaluation_logs")
    work = relationship("Work", back_populates="evaluation_logs")


def _validate_evaluation_log_target(
    mapper, connection, target: EvaluationLog
) -> None:
    if target.generation_task_id is None and target.work_id is None:
        raise ValueError(
            "evaluation_logs requires generation_task_id or work_id to be set"
        )


event.listen(EvaluationLog, "before_insert", _validate_evaluation_log_target)
event.listen(EvaluationLog, "before_update", _validate_evaluation_log_target)
