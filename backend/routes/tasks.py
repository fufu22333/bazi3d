from flask import Blueprint, g, jsonify, request

from backend.routes.auth import require_auth
from backend.services.guardrails import (
    ApiError,
    build_error_response,
    validate_task_payload,
)
from backend.services.task_service import (
    create_task_for_user,
    get_task_for_user,
    serialize_task,
)

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@tasks_bp.post("")
@require_auth
def create_task():
    payload = request.get_json(silent=True)
    try:
        payload = validate_task_payload(payload)
        task = create_task_for_user(g.current_user, payload)
    except ApiError as exc:
        return build_error_response(exc)
    return jsonify(serialize_task(task)), 201


@tasks_bp.get("/<int:task_id>")
@require_auth
def get_task(task_id: int):
    task = get_task_for_user(task_id, g.current_user)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(serialize_task(task)), 200
