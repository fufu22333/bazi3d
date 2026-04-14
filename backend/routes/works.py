from flask import Blueprint, g, jsonify, request

from backend.routes.auth import get_optional_auth_user, require_auth
from backend.services.guardrails import (
    ApiError,
    build_error_response,
    validate_work_payload,
    validate_work_update_payload,
)
from backend.services.work_service import (
    WorkNotFoundError,
    WorkPermissionError,
    create_work_for_user,
    delete_work_for_user,
    get_work_detail_for_user,
    list_public_works,
    list_user_works,
    serialize_work,
    update_work_for_user,
)

works_bp = Blueprint("works", __name__, url_prefix="/api/works")


@works_bp.post("")
@require_auth
def create_work():
    payload = request.get_json(silent=True)
    try:
        payload = validate_work_payload(payload)
        work = create_work_for_user(g.current_user, payload)
    except ApiError as exc:
        return build_error_response(exc)
    except ValueError as exc:
        return build_error_response(ApiError(400, "invalid_request", str(exc)))
    except WorkNotFoundError as exc:
        return build_error_response(ApiError(404, "not_found", str(exc)))
    except WorkPermissionError as exc:
        return build_error_response(ApiError(403, "forbidden", str(exc)))

    return jsonify(serialize_work(work)), 201


@works_bp.get("")
def list_works():
    items = [serialize_work(work) for work in list_public_works()]
    return jsonify({"items": items}), 200


@works_bp.get("/mine")
@require_auth
def list_my_works():
    items = [serialize_work(work) for work in list_user_works(g.current_user)]
    return jsonify({"items": items}), 200


@works_bp.get("/<int:work_id>")
def get_work_detail(work_id: int):
    current_user = None
    try:
        current_user = get_optional_auth_user()
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401

    work = get_work_detail_for_user(work_id, current_user)
    if work is None:
        return jsonify({"error": "Work not found"}), 404

    return jsonify(serialize_work(work)), 200


@works_bp.patch("/<int:work_id>")
@require_auth
def update_work(work_id: int):
    payload = request.get_json(silent=True)
    try:
        payload = validate_work_update_payload(payload)
        work = update_work_for_user(work_id, g.current_user, payload)
    except ApiError as exc:
        return build_error_response(exc)
    except WorkNotFoundError as exc:
        return build_error_response(ApiError(404, "not_found", str(exc)))
    except WorkPermissionError as exc:
        return build_error_response(ApiError(403, "forbidden", str(exc)))

    return jsonify(serialize_work(work)), 200


@works_bp.delete("/<int:work_id>")
@require_auth
def delete_work(work_id: int):
    try:
        delete_work_for_user(work_id, g.current_user)
    except WorkNotFoundError as exc:
        return build_error_response(ApiError(404, "not_found", str(exc)))
    except WorkPermissionError as exc:
        return build_error_response(ApiError(403, "forbidden", str(exc)))

    return "", 204
