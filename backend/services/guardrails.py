import json
from typing import Any, Callable

from flask import current_app, g, jsonify

from backend.prompt.builder import generate_prompt_output
from backend.prompt.schema import PromptOutput


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        task_id: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.task_id = task_id


def log_structured_event(
    logger,
    level: str,
    event: str,
    request_id: str | None,
    task_id: int | None,
    **fields,
) -> None:
    payload = {
        "event": event,
        "request_id": request_id,
        "task_id": task_id,
        **fields,
    }
    getattr(logger, level)(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def build_error_response(error: ApiError):
    request_id = getattr(g, "request_id", None)
    log_structured_event(
        current_app.logger,
        "warning",
        "api_error",
        request_id=request_id,
        task_id=error.task_id,
        code=error.code,
        message=error.message,
    )
    payload = {
        "error": {
            "code": error.code,
            "message": error.message,
            "request_id": request_id,
            "task_id": error.task_id,
        }
    }
    response = jsonify(payload)
    response.status_code = error.status_code
    return response


def ensure_json_object(payload: Any) -> dict:
    if not isinstance(payload, dict):
        raise ApiError(400, "invalid_request", "request body must be a JSON object")
    return payload


def validate_task_payload(payload: Any) -> dict:
    payload = ensure_json_object(payload)
    display_name = payload.get("display_name")
    style_profile = payload.get("style_profile")
    extra_payload = payload.get("extra_payload")

    if not isinstance(display_name, str) or not display_name.strip():
        raise ApiError(400, "invalid_request", "display_name is required")
    if style_profile is not None and not isinstance(style_profile, dict):
        raise ApiError(400, "invalid_request", "style_profile must be an object")
    if extra_payload is not None and not isinstance(extra_payload, dict):
        raise ApiError(400, "invalid_request", "extra_payload must be an object")
    return payload


def validate_asset_import_payload(payload: Any) -> dict:
    payload = ensure_json_object(payload)
    source_url = payload.get("source_url")
    file_format = payload.get("file_format")
    metadata = payload.get("metadata")

    if not isinstance(source_url, str) or not source_url.strip():
        raise ApiError(400, "invalid_request", "source_url is required")
    if not isinstance(file_format, str) or not file_format.strip():
        raise ApiError(400, "invalid_request", "file_format is required")
    if metadata is not None and not isinstance(metadata, dict):
        raise ApiError(400, "invalid_request", "metadata must be an object")
    return payload


def validate_work_payload(payload: Any) -> dict:
    payload = ensure_json_object(payload)
    asset_id = payload.get("asset_id")
    title = payload.get("title")
    visibility = payload.get("visibility")

    if not isinstance(asset_id, int):
        raise ApiError(400, "invalid_request", "asset_id is required")
    if not isinstance(title, str) or not title.strip():
        raise ApiError(400, "invalid_request", "title is required")
    if visibility is not None and visibility not in {"public", "private"}:
        raise ApiError(
            400, "invalid_request", "visibility must be public or private"
        )
    return payload


def validate_work_update_payload(payload: Any) -> dict:
    payload = ensure_json_object(payload)

    allowed_keys = {"title", "description", "visibility", "allow_remix"}
    if not payload:
        raise ApiError(400, "invalid_request", "at least one field is required")
    unknown_keys = set(payload.keys()) - allowed_keys
    if unknown_keys:
        raise ApiError(400, "invalid_request", "unsupported work update field")

    title = payload.get("title")
    visibility = payload.get("visibility")
    allow_remix = payload.get("allow_remix")

    if title is not None and (not isinstance(title, str) or not title.strip()):
        raise ApiError(400, "invalid_request", "title must be a non-empty string")
    if "description" in payload and payload["description"] is not None and not isinstance(
        payload["description"], str
    ):
        raise ApiError(400, "invalid_request", "description must be a string or null")
    if visibility is not None and visibility not in {"public", "private"}:
        raise ApiError(400, "invalid_request", "visibility must be public or private")
    if allow_remix is not None and not isinstance(allow_remix, bool):
        raise ApiError(400, "invalid_request", "allow_remix must be a boolean")

    return payload


def validate_evaluation_payload(payload: Any) -> dict:
    payload = ensure_json_object(payload)
    generation_task_id = payload.get("generation_task_id")
    work_id = payload.get("work_id")
    level = payload.get("level")
    metrics = payload.get("metrics")

    if generation_task_id is None and work_id is None:
        raise ApiError(
            400,
            "invalid_request",
            "generation_task_id or work_id is required",
        )
    if level not in {"text", "3d", "pipeline"}:
        raise ApiError(
            400,
            "invalid_request",
            "level must be one of: text, 3d, pipeline",
            task_id=generation_task_id,
        )
    if not isinstance(metrics, dict):
        raise ApiError(
            400,
            "invalid_request",
            "metrics must be an object",
            task_id=generation_task_id,
        )
    return payload


def safe_generate_prompt_output(
    input_profile: dict,
    llm_callable: Callable[[str], str],
    logger,
    request_id: str | None,
    task_id: int | None,
) -> PromptOutput:
    try:
        return generate_prompt_output(input_profile, llm_callable)
    except Exception as exc:
        style_profile = input_profile.get("style_profile") or {}
        fallback = {
            "version": "fallback-v1",
            "character": {
                "style": style_profile.get("fashion_style") or "default",
                "material": "fallback-material",
                "pose_keywords": ["idle"],
                "visual_keywords": ["fallback"],
                "description": "Fallback character prompt output.",
            },
            "guardian_spirit": {
                "style": style_profile.get("spirit_style") or "default",
                "material": "fallback-material",
                "pose_keywords": ["idle"],
                "visual_keywords": ["fallback"],
                "description": "Fallback guardian prompt output.",
            },
        }
        log_structured_event(
            logger,
            "warning",
            "llm_fallback",
            request_id=request_id,
            task_id=task_id,
            error=str(exc),
        )
        return PromptOutput.model_validate(fallback)


def safe_normalize_model_output(
    adapter,
    result: dict,
    logger,
    request_id: str | None,
    task_id: int | None,
) -> dict:
    try:
        return adapter.normalize(result)
    except Exception as exc:
        fallback_url = None
        if isinstance(result, dict):
            if isinstance(result.get("url"), str) and result["url"]:
                fallback_url = result["url"]
            model_urls = result.get("model_urls")
            if fallback_url is None and isinstance(model_urls, dict):
                candidate = model_urls.get("glb")
                if isinstance(candidate, str) and candidate:
                    fallback_url = candidate

        if fallback_url is None:
            raise

        log_structured_event(
            logger,
            "warning",
            "model_output_fallback",
            request_id=request_id,
            task_id=task_id,
            error=str(exc),
        )
        return {
            "url": fallback_url,
            "format": "glb",
            "metadata": {
                "fallback": True,
                "task_id": task_id,
            },
        }
