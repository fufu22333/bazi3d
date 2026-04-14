from backend.models import SessionLocal
from backend.models.evaluation_log import EvaluationLog
from backend.models.generation_task import GenerationTask
from backend.models.user import User
from backend.models.work import Work

ALLOWED_LEVELS = {"text", "3d", "pipeline"}


class EvaluationPermissionError(Exception):
    pass


class EvaluationTargetNotFoundError(Exception):
    pass


def create_evaluation_log_for_user(user: User, payload: dict) -> EvaluationLog:
    generation_task_id = payload.get("generation_task_id")
    work_id = payload.get("work_id")
    level = payload.get("level")
    metrics = payload.get("metrics")
    subjective_score = payload.get("subjective_score")

    if generation_task_id is None and work_id is None:
        raise ValueError("generation_task_id or work_id is required")
    if level not in ALLOWED_LEVELS:
        raise ValueError("level must be one of: text, 3d, pipeline")
    if not isinstance(metrics, dict):
        raise ValueError("metrics must be an object")

    session = SessionLocal()

    if generation_task_id is not None:
        task = session.query(GenerationTask).filter_by(id=generation_task_id).first()
        if task is None:
            raise EvaluationTargetNotFoundError("Generation task not found")
        if task.user_id != user.id:
            raise EvaluationPermissionError("Forbidden")

    if work_id is not None:
        work = session.query(Work).filter_by(id=work_id).first()
        if work is None:
            raise EvaluationTargetNotFoundError("Work not found")
        if work.user_id != user.id:
            raise EvaluationPermissionError("Forbidden")

    log = EvaluationLog(
        generation_task_id=generation_task_id,
        work_id=work_id,
        level=level,
        metrics=metrics,
        subjective_score=subjective_score,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def list_evaluation_logs_for_user(
    user: User, generation_task_id: int | None = None, work_id: int | None = None
) -> list[EvaluationLog]:
    if generation_task_id is None and work_id is None:
        raise ValueError("generation_task_id or work_id is required")

    session = SessionLocal()
    query = session.query(EvaluationLog)

    if generation_task_id is not None:
        task = session.query(GenerationTask).filter_by(id=generation_task_id).first()
        if task is None:
            raise EvaluationTargetNotFoundError("Generation task not found")
        if task.user_id != user.id:
            raise EvaluationPermissionError("Forbidden")
        query = query.filter_by(generation_task_id=generation_task_id)

    if work_id is not None:
        work = session.query(Work).filter_by(id=work_id).first()
        if work is None:
            raise EvaluationTargetNotFoundError("Work not found")
        if work.user_id != user.id:
            raise EvaluationPermissionError("Forbidden")
        query = query.filter_by(work_id=work_id)

    return query.order_by(EvaluationLog.created_at.desc()).all()


def serialize_evaluation_log(log: EvaluationLog) -> dict:
    return {
        "id": log.id,
        "generation_task_id": log.generation_task_id,
        "work_id": log.work_id,
        "level": log.level,
        "metrics": log.metrics,
        "subjective_score": log.subjective_score,
        "created_at": log.created_at.isoformat(),
    }
