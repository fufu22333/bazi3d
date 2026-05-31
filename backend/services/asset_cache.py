from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urlparse

import requests
from flask import current_app


LOGGER = logging.getLogger(__name__)


def _frontend_dir() -> Path:
    configured_dir = current_app.config.get("FRONTEND_DIR")
    if configured_dir:
        return Path(configured_dir)
    return Path(current_app.root_path).parent / "frontend"


def _asset_cache_dir() -> Path:
    configured_dir = current_app.config.get("GENERATED_ASSET_CACHE_DIR")
    if configured_dir:
        return Path(configured_dir)
    return _frontend_dir() / "assets" / "generated"


def _public_asset_url(path: Path) -> str:
    relative_path = path.relative_to(_frontend_dir()).as_posix()
    return f"/{relative_path}"


def _extension_from_url(url: str, fallback: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    return fallback


def _download_to_file(url: str, path: Path) -> None:
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    path.write_bytes(response.content)


def cache_generated_asset(
    task_id: int,
    asset_type: str,
    normalized: dict,
) -> dict:
    source_url = normalized.get("url")
    if not isinstance(source_url, str) or not source_url:
        return normalized
    if source_url.startswith("/") or source_url.startswith("./"):
        return normalized

    cache_dir = _asset_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    file_format = str(normalized.get("format") or "glb").lower().lstrip(".")
    model_path = cache_dir / f"task{task_id}-{asset_type}.{file_format}"
    metadata = dict(normalized.get("metadata") or {})

    try:
        _download_to_file(source_url, model_path)
    except requests.RequestException:
        LOGGER.exception("Failed to cache generated model asset for task %s", task_id)
        return normalized

    cached_metadata = {
        **metadata,
        "source_url": source_url,
    }

    thumbnail_url = metadata.get("thumbnail_url")
    if isinstance(thumbnail_url, str) and thumbnail_url:
        preview_ext = _extension_from_url(thumbnail_url, ".png")
        preview_path = cache_dir / f"task{task_id}-{asset_type}-preview{preview_ext}"
        try:
            _download_to_file(thumbnail_url, preview_path)
            cached_metadata["source_thumbnail_url"] = thumbnail_url
            cached_metadata["thumbnail_url"] = _public_asset_url(preview_path)
        except requests.RequestException:
            LOGGER.exception("Failed to cache generated preview for task %s", task_id)

    return {
        **normalized,
        "url": _public_asset_url(model_path),
        "metadata": cached_metadata,
    }
