from flask import Blueprint, g, jsonify, request

from backend.routes.auth import require_auth
from backend.services.evaluation_service import (
    EvaluationPermissionError,
    EvaluationTargetNotFoundError,
    create_evaluation_log_for_user,
    list_evaluation_logs_for_user,
    serialize_evaluation_log,
)
from backend.services.guardrails import (
    ApiError,
    build_error_response,
    validate_evaluation_payload,
)

evaluations_bp = Blueprint("evaluations", __name__, url_prefix="/api/evaluations")


@evaluations_bp.post("")
@require_auth
def create_evaluation():
    payload = request.get_json(silent=True)
    try:
        payload = validate_evaluation_payload(payload)
        log = create_evaluation_log_for_user(g.current_user, payload)
    except ApiError as exc:
        return build_error_response(exc)
    except ValueError as exc:
        return build_error_response(ApiError(400, "invalid_request", str(exc)))
    except EvaluationTargetNotFoundError as exc:
        return build_error_response(
            ApiError(
                404,
                "not_found",
                str(exc),
                task_id=payload.get("generation_task_id") if isinstance(payload, dict) else None,
            )
        )
    except EvaluationPermissionError as exc:
        return build_error_response(
            ApiError(
                403,
                "forbidden",
                str(exc),
                task_id=payload.get("generation_task_id") if isinstance(payload, dict) else None,
            )
        )

    return jsonify(serialize_evaluation_log(log)), 201


@evaluations_bp.get("")
@require_auth
def list_evaluations():
    generation_task_id = request.args.get("generation_task_id", type=int)
    work_id = request.args.get("work_id", type=int)

    try:
        items = list_evaluation_logs_for_user(
            g.current_user,
            generation_task_id=generation_task_id,
            work_id=work_id,
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except EvaluationTargetNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except EvaluationPermissionError as exc:
        return jsonify({"error": str(exc)}), 403

    return jsonify({"items": [serialize_evaluation_log(item) for item in items]}), 200
