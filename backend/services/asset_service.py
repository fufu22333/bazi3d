from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from backend.models import SessionLocal
from backend.models.generation_task import GenerationTask
from backend.models.input_profile import InputProfile
from backend.models.model_asset import ModelAsset
from backend.models.user import User


class AssetNotFoundError(Exception):
    pass


class AssetPermissionError(Exception):
    pass


def _signed_url_expiry_timestamp(url: str | None) -> int | None:
    if not url:
        return None
    query = parse_qs(urlparse(url).query)
    sign_time_values = query.get("q-sign-time")
    if not sign_time_values:
        return None
    parts = sign_time_values[0].split(";")
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _is_signed_url_expired(url: str | None) -> bool:
    expiry_timestamp = _signed_url_expiry_timestamp(url)
    if expiry_timestamp is None:
        return False
    return expiry_timestamp <= int(datetime.now(timezone.utc).timestamp())


def import_asset_for_user(user: User, payload: dict) -> ModelAsset:
    source_url = payload.get("source_url")
    file_format = payload.get("file_format")
    metadata = payload.get("metadata")

    if not source_url:
        raise ValueError("source_url is required")
    if not file_format:
        raise ValueError("file_format is required")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")

    session = SessionLocal()

    profile = InputProfile(
        user_id=user.id,
        extra_payload={"source": "asset_import"},
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)

    task = GenerationTask(
        user_id=user.id,
        input_profile_id=profile.id,
        status="completed",
        provider="import",
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    asset = ModelAsset(
        generation_task_id=task.id,
        asset_type="imported",
        storage_url=source_url,
        file_format=file_format,
        asset_metadata=metadata,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def serialize_asset(asset: ModelAsset) -> dict:
    metadata = dict(asset.asset_metadata or {})
    is_signed_url_expired = _is_signed_url_expired(asset.storage_url)
    thumbnail_url = metadata.get("thumbnail_url")
    thumbnail_expired = _is_signed_url_expired(thumbnail_url)
    metadata["thumbnail_available"] = bool(thumbnail_url) and not thumbnail_expired
    viewer_type = "guardian" if asset.asset_type == "guardian_spirit" else "person"

    return {
        "id": asset.id,
        "asset_type": asset.asset_type,
        "type": viewer_type,
        "url": asset.storage_url,
        "format": asset.file_format,
        "metadata": metadata,
        "is_available": bool(asset.storage_url) and not is_signed_url_expired,
        "is_signed_url_expired": is_signed_url_expired,
    }


def get_asset_for_user(asset_id: int, user: User) -> ModelAsset:
    session = SessionLocal()
    asset = session.query(ModelAsset).filter_by(id=asset_id).first()
    if asset is None:
        raise AssetNotFoundError("Asset not found")
    if asset.generation_task.user_id != user.id:
        raise AssetPermissionError("Forbidden")
    return asset


def delete_asset_for_user(asset_id: int, user: User) -> None:
    session = SessionLocal()
    asset = session.query(ModelAsset).filter_by(id=asset_id).first()
    if asset is None:
        raise AssetNotFoundError("Asset not found")
    if asset.generation_task.user_id != user.id:
        raise AssetPermissionError("Forbidden")

    session.delete(asset)
    session.commit()
