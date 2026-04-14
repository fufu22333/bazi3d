from backend.models import SessionLocal
from backend.models.model_asset import ModelAsset
from backend.models.user import User
from backend.models.work import Work
from backend.services.asset_service import serialize_asset


class WorkPermissionError(Exception):
    pass


class WorkNotFoundError(Exception):
    pass


def _extract_style_tags(work: Work) -> list[str]:
    profile = getattr(work.primary_asset.generation_task, "input_profile", None)
    if profile is None or not profile.style_profile:
        return []

    style_profile = profile.style_profile or {}
    tags = []
    for key in ("fashion_style", "spirit_style"):
        value = style_profile.get(key)
        if isinstance(value, str) and value.strip():
            tags.append(value.strip())
    return tags


def _serialize_author(work: Work) -> dict:
    return {
        "id": work.user.id,
        "username": work.user.username,
    }


def create_work_for_user(user: User, payload: dict) -> Work:
    asset_id = payload.get("asset_id")
    title = payload.get("title")
    description = payload.get("description")
    visibility = payload.get("visibility") or "private"
    allow_remix = bool(payload.get("allow_remix", False))

    if not asset_id:
        raise ValueError("asset_id is required")
    if not title:
        raise ValueError("title is required")
    if visibility not in {"public", "private"}:
        raise ValueError("visibility must be public or private")

    session = SessionLocal()
    asset = session.query(ModelAsset).filter_by(id=asset_id).first()
    if asset is None:
        raise WorkNotFoundError("Asset not found")
    if asset.generation_task.user_id != user.id:
        raise WorkPermissionError("Forbidden")

    work = Work(
        user_id=user.id,
        primary_asset_id=asset.id,
        title=title,
        description=description,
        visibility=visibility,
        allow_remix=allow_remix,
    )
    session.add(work)
    session.commit()
    session.refresh(work)
    return work


def serialize_work(work: Work) -> dict:
    return {
        "id": work.id,
        "title": work.title,
        "description": work.description,
        "visibility": work.visibility,
        "allow_remix": work.allow_remix,
        "asset": serialize_asset(work.primary_asset),
        "author": _serialize_author(work),
        "created_at": work.created_at.isoformat(),
        "style_tags": _extract_style_tags(work),
    }


def list_public_works() -> list[Work]:
    session = SessionLocal()
    return (
        session.query(Work)
        .filter_by(visibility="public")
        .order_by(Work.created_at.desc())
        .all()
    )


def list_user_works(user: User) -> list[Work]:
    session = SessionLocal()
    return (
        session.query(Work)
        .filter_by(user_id=user.id)
        .order_by(Work.created_at.desc())
        .all()
    )


def get_public_work_detail(work_id: int) -> Work | None:
    session = SessionLocal()
    return (
        session.query(Work)
        .filter_by(id=work_id, visibility="public")
        .first()
    )


def get_work_detail_for_user(work_id: int, user: User | None) -> Work | None:
    session = SessionLocal()
    work = session.query(Work).filter_by(id=work_id).first()
    if work is None:
        return None
    if work.visibility == "public":
        return work
    if user is not None and work.user_id == user.id:
        return work
    return None


def update_work_for_user(work_id: int, user: User, payload: dict) -> Work:
    session = SessionLocal()
    work = session.query(Work).filter_by(id=work_id).first()
    if work is None:
        raise WorkNotFoundError("Work not found")
    if work.user_id != user.id:
        raise WorkPermissionError("Forbidden")

    if "title" in payload:
        work.title = payload["title"].strip()
    if "description" in payload:
        work.description = payload["description"]
    if "visibility" in payload:
        work.visibility = payload["visibility"]
    if "allow_remix" in payload:
        work.allow_remix = payload["allow_remix"]

    session.commit()
    session.refresh(work)
    return work


def delete_work_for_user(work_id: int, user: User) -> None:
    session = SessionLocal()
    work = session.query(Work).filter_by(id=work_id).first()
    if work is None:
        raise WorkNotFoundError("Work not found")
    if work.user_id != user.id:
        raise WorkPermissionError("Forbidden")

    session.delete(work)
    session.commit()
