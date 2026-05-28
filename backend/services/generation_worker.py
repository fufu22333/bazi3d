from __future__ import annotations

import json
import logging
import traceback
from pathlib import Path
from typing import Any

from flask import current_app

from backend.adapters.hunyuan3d_adapter import Hunyuan3DAdapter
from backend.adapters.provider_registry import ProviderRegistry
from backend.models import SessionLocal
from backend.models.generation_task import GenerationTask
from backend.models.model_asset import ModelAsset
from backend.prompt.llm_client import DeepSeekClient
from backend.services.guardrails import (
    safe_generate_prompt_output,
    safe_normalize_model_output,
)


LOGGER = logging.getLogger(__name__)
ASSET_PROMPT_FIELDS = {
    "character": "character",
    "guardian_spirit": "guardian_spirit",
}
PROVIDER_KEY = "hunyuan3d"


def _serialize_input_profile(profile) -> dict[str, Any]:
    extra_payload = profile.extra_payload or {}
    payload = {
        "display_name": profile.display_name,
        "gender": profile.gender,
        "birth_location": profile.birth_location,
        "birth_datetime": profile.birth_datetime.isoformat()
        if profile.birth_datetime
        else extra_payload.get("birth_datetime", ""),
        "style_profile": profile.style_profile or {},
        "extra_payload": extra_payload,
        "reference_image_url": profile.reference_image_url,
    }
    return payload


def _build_asset_prompt(asset_key: str, section, input_profile: dict[str, Any]) -> str:
    display_name = input_profile.get("display_name") or "the character"
    gender = input_profile.get("gender") or "unspecified"
    birth_location = input_profile.get("birth_location") or "unknown"
    birth_datetime = input_profile.get("birth_datetime") or "unknown"
    pose_keywords = ", ".join(section.pose_keywords)
    visual_keywords = ", ".join(section.visual_keywords)

    role_label = "3D character" if asset_key == "character" else "guardian spirit"
    geometry_constraints = (
        "Mandatory geometry constraints: complete full-body human figure from head to feet; "
        "visible full legs, feet and footwear; standing full-body composition; "
        "not a bust; not a half-body; not a portrait; not cropped at waist or knees."
        if asset_key == "character"
        else (
            "Mandatory geometry constraints: complete full-body non-human companion creature; "
            "visible head, torso, limbs or paws, and tail if present; not a bust; "
            "not a half-body; not a portrait; not cropped."
        )
    )
    return (
        f"Create a high-quality stylized {role_label} as a GLB-ready 3D model.\n"
        f"{geometry_constraints}\n"
        f"Subject name: {display_name}\n"
        f"Gender presentation: {gender}\n"
        f"Birth location: {birth_location}\n"
        f"Birth datetime: {birth_datetime}\n"
        f"Style: {section.style}\n"
        f"Material: {section.material}\n"
        f"Pose keywords: {pose_keywords}\n"
        f"Visual keywords: {visual_keywords}\n"
        f"Description: {section.description}\n"
        "Output should emphasize complete character silhouette, readable forms, and clean 3D details."
    )


def _prompt_output_to_dict(prompt_output: Any) -> dict[str, Any]:
    if hasattr(prompt_output, "model_dump"):
        return prompt_output.model_dump()
    if hasattr(prompt_output, "dict"):
        return prompt_output.dict()
    return dict(prompt_output)


def _prompt_for_submit(adapter, prompt: str) -> str:
    truncate = getattr(adapter, "_truncate_prompt", None)
    if callable(truncate):
        return truncate(prompt)
    return prompt


def _write_prompt_debug_artifact(
    *,
    task_id: int,
    input_profile: dict[str, Any],
    prompt_output,
    asset_prompts: dict[str, dict[str, str]],
) -> None:
    debug_dir = current_app.config.get("PROMPT_DEBUG_DIR") or "output/debug_prompts"
    path = Path(debug_dir)
    path.mkdir(parents=True, exist_ok=True)
    payload = {
        "task_id": task_id,
        "input_profile": input_profile,
        "prompt_output": _prompt_output_to_dict(prompt_output),
        "asset_prompts": asset_prompts,
    }
    (path / f"task-{task_id}-prompts.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _build_provider_registry() -> ProviderRegistry:
    config = current_app.config
    registry = ProviderRegistry()
    adapter = Hunyuan3DAdapter(
        secret_id=config.get("TENCENTCLOUD_SECRET_ID", ""),
        secret_key=config.get("TENCENTCLOUD_SECRET_KEY", ""),
        region=config.get("TENCENTCLOUD_REGION", "ap-guangzhou"),
        endpoint=config.get("HUNYUAN_ENDPOINT", ""),
    )
    registry.register(PROVIDER_KEY, adapter)
    return registry


def _create_llm_client() -> DeepSeekClient:
    return DeepSeekClient()


def _persist_assets(
    session,
    task: GenerationTask,
    normalized_assets: list[tuple[str, str, dict[str, Any]]],
) -> None:
    for asset_type, job_id, normalized in normalized_assets:
        session.add(
            ModelAsset(
                generation_task_id=task.id,
                asset_type=asset_type,
                storage_url=normalized["url"],
                file_format=normalized["format"],
                asset_metadata=normalized["metadata"],
            )
        )
        if asset_type == "character":
            task.character_task_ref = job_id
            task.external_task_id = job_id
        if asset_type == "guardian_spirit":
            task.spirit_task_ref = job_id


def _mark_task_failed(session, task_id: int, exc: Exception) -> GenerationTask:
    session.rollback()
    task = session.get(GenerationTask, task_id)
    traceback.print_exc()
    if task is None:
        raise ValueError(f"GenerationTask {task_id} not found") from exc
    task.status = "failed"
    task.error_message = str(exc)
    session.commit()
    return task


def run_generation_task(task_id: int) -> GenerationTask:
    session = SessionLocal()
    try:
        task = session.get(GenerationTask, task_id)
        if task is None:
            raise ValueError(f"GenerationTask {task_id} not found")

        profile = task.input_profile
        input_profile = _serialize_input_profile(profile)

        llm_client = _create_llm_client()
        prompt_output = safe_generate_prompt_output(
            input_profile=input_profile,
            llm_callable=lambda prompt: llm_client.generate_json(prompt),
            logger=current_app.logger,
            request_id=None,
            task_id=task.id,

        )
        print("LLM output:", prompt_output)

        provider_registry = _build_provider_registry()
        adapter = provider_registry.get(PROVIDER_KEY)

        normalized_assets: list[tuple[str, str, dict[str, Any]]] = []
        asset_prompts: dict[str, dict[str, str]] = {}
        for asset_type, prompt_field in ASSET_PROMPT_FIELDS.items():
            section = getattr(prompt_output, prompt_field)
            prompt = _build_asset_prompt(asset_type, section, input_profile)
            asset_prompts[asset_type] = {
                "full_prompt": prompt,
                "submitted_prompt": _prompt_for_submit(adapter, prompt),
            }

        _write_prompt_debug_artifact(
            task_id=task.id,
            input_profile=input_profile,
            prompt_output=prompt_output,
            asset_prompts=asset_prompts,
        )

        for asset_type in ASSET_PROMPT_FIELDS:
            prompt = asset_prompts[asset_type]["full_prompt"]
            job_id = adapter.submit_job(prompt)
            raw_result = adapter.query_job(job_id)
            normalized = safe_normalize_model_output(
                adapter=adapter,
                result=raw_result,
                logger=current_app.logger,
                request_id=None,
                task_id=task.id,
            )
            normalized_assets.append((asset_type, job_id, normalized))

        _persist_assets(session, task, normalized_assets)
        task.provider = "hunyuan3d"
        task.status = "completed"
        task.error_message = None
        session.commit()
        task.model_assets
        return task
    except Exception as exc:
        return _mark_task_failed(session, task_id, exc)
    finally:
        session.close()
        SessionLocal.remove()
