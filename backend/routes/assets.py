from flask import Blueprint, g, jsonify, request

from backend.routes.auth import require_auth
from backend.services.asset_service import (
    AssetNotFoundError,
    AssetPermissionError,
    delete_asset_for_user,
    get_asset_for_user,
    import_asset_for_user,
    serialize_asset,
)
from backend.services.guardrails import (
    ApiError,
    build_error_response,
    validate_asset_import_payload,
)

assets_bp = Blueprint("assets", __name__, url_prefix="/api/assets")


@assets_bp.post("/import")
@require_auth
def import_asset():
    payload = request.get_json(silent=True)
    try:
        payload = validate_asset_import_payload(payload)
        asset = import_asset_for_user(g.current_user, payload)
    except ApiError as exc:
        return build_error_response(exc)
    except ValueError as exc:
        return build_error_response(ApiError(400, "invalid_request", str(exc)))

    return jsonify(serialize_asset(asset)), 201


@assets_bp.get("/<int:asset_id>")
@require_auth
def get_asset(asset_id: int):
    try:
        asset = get_asset_for_user(asset_id, g.current_user)
    except AssetNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except AssetPermissionError as exc:
        return jsonify({"error": str(exc)}), 403

    return jsonify(serialize_asset(asset)), 200


@assets_bp.delete("/<int:asset_id>")
@require_auth
def delete_asset(asset_id: int):
    try:
        delete_asset_for_user(asset_id, g.current_user)
    except AssetNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except AssetPermissionError as exc:
        return jsonify({"error": str(exc)}), 403

    return "", 204
