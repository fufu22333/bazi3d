from __future__ import annotations

import threading
from datetime import datetime

from flask import current_app

from backend.models import SessionLocal
from backend.models.generation_task import GenerationTask
from backend.models.input_profile import InputProfile
from backend.models.user import User
from backend.services.generation_worker import run_generation_task


def _parse_birth_datetime(value) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _run_generation_with_app(app, task_id: int) -> None:
    with app.app_context():
        run_generation_task(task_id)


def _start_generation_thread(task_id: int) -> None:
    app = current_app._get_current_object()
    worker = threading.Thread(
        target=_run_generation_with_app,
        args=(app, task_id),
        name=f"generation-task-{task_id}",
        daemon=True,
    )
    worker.start()


def create_task_for_user(user: User, payload: dict) -> GenerationTask:
    session = SessionLocal()
    try:
        extra_payload = payload.get("extra_payload") or {}
        profile = InputProfile(
            user_id=user.id,
            display_name=payload.get("display_name"),
            gender=payload.get("gender"),
            birth_datetime=_parse_birth_datetime(
                payload.get("birth_datetime") or extra_payload.get("birth_datetime")
            ),
            calendar_type=payload.get("calendar_type") or extra_payload.get("calendar_type"),
            birth_location=payload.get("birth_location"),
            style_profile=payload.get("style_profile"),
            extra_payload=payload.get("extra_payload"),
            reference_image_url=payload.get("reference_image_url"),
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)

        task = GenerationTask(
            user_id=user.id,
            input_profile_id=profile.id,
            status="pending",
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        task.model_assets
        session.expunge(task)
    finally:
        session.close()

    _start_generation_thread(task.id)
    return task


def serialize_task(task: GenerationTask) -> dict:
    return {
        "id": task.id,
        "status": task.status,
        "provider": task.provider,
        "assets": [
            {
                "id": asset.id,
                "asset_type": asset.asset_type,
                "storage_url": asset.storage_url,
                "file_format": asset.file_format,
                "metadata": asset.asset_metadata,
                "type": "person" if asset.asset_type == "character" else "guardian",
                "url": asset.storage_url,
            }
            for asset in sorted(task.model_assets, key=lambda item: item.id)
        ],
    }


def get_task_for_user(task_id: int, user: User) -> GenerationTask | None:
    session = SessionLocal()
    try:
        task = (
            session.query(GenerationTask)
            .filter_by(id=task_id, user_id=user.id)
            .first()
        )
        if task is None:
            return None
        task.model_assets
        session.expunge(task)
        return task
    finally:
        session.close()
