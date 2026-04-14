from flask import Blueprint, current_app, g, jsonify, request

from backend.routes.auth import require_auth
from backend.services.chat_service import generate_character_reply
from backend.services.guardrails import ApiError, build_error_response

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.post("")
@require_auth
def chat():
    payload = request.get_json(silent=True)
    try:
        result = generate_character_reply(
            payload=payload,
            logger=current_app.logger,
            request_id=getattr(g, "request_id", None),
            llm_callable=current_app.config.get("CHAT_LLM_CALLABLE"),
        )
    except ApiError as exc:
        return build_error_response(exc)

    return jsonify(result), 200
