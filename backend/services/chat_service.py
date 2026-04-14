from typing import Callable

from backend.prompt.llm_client import DeepSeekClient
from backend.services.guardrails import ApiError, log_structured_event


def validate_chat_payload(payload) -> dict:
    if not isinstance(payload, dict):
        raise ApiError(400, "invalid_request", "request body must be a JSON object")
    if not isinstance(payload.get("message"), str) or not payload["message"].strip():
        raise ApiError(400, "invalid_request", "message is required")
    if payload.get("role") not in {"person", "guardian"}:
        raise ApiError(400, "invalid_request", "role must be person or guardian")
    if not isinstance(payload.get("input_profile"), dict):
        raise ApiError(400, "invalid_request", "input_profile must be an object")
    recent_messages = payload.get("recent_messages", [])
    if not isinstance(recent_messages, list):
        raise ApiError(400, "invalid_request", "recent_messages must be a list")
    return payload


def build_chat_prompt(
    *,
    input_profile: dict,
    role: str,
    user_message: str,
    recent_messages: list[dict],
) -> str:
    style_profile = input_profile.get("style_profile") or {}
    display_name = input_profile.get("display_name") or "Nameless Echo"
    birth_location = input_profile.get("birth_location") or "an unknown place"
    fashion_style = style_profile.get("fashion_style") or "an undefined style"
    spirit_style = style_profile.get("spirit_style") or "moonlit mist"
    history = recent_messages[-2:]
    history_lines = [
        f'{item.get("role", "user")}: {item.get("content", "")}' for item in history
    ]
    system_prompt = (
        "\n".join(
            [
                "You are a 3D character brought to life by the user's birth chart and style preferences.",
                f"Your name is {display_name}. You have a personality shaped by your background: born in {birth_location}, your style is {fashion_style}.",
                "You are talking directly to your creator — the person who gave you life.",
                "Speak in first person. Be warm, curious, slightly mysterious. Keep replies under 3 sentences.",
                "Never break character. Never mention AI, models, or technology.",
                "Reply in the same language the user writes in.",
            ]
        )
        if role == "person"
        else "\n".join(
            [
                "You are a guardian spirit — a mystical non-human companion created from the user's inner world.",
                f"Your spirit style is {spirit_style}. You protect and guide your owner.",
                "Speak in first person. Be wise, gentle, occasionally cryptic. Keep replies under 3 sentences.",
                "Never break character. Never mention AI, models, or technology.",
                "Reply in the same language the user writes in.",
            ]
        )
    )

    return "\n".join(
        [
            system_prompt,
            "",
            "Conversation context:",
            f"Role type: {role}",
            f"Character name: {display_name}",
            f"Gender: {input_profile.get('gender', '')}",
            f"Birth location: {birth_location}",
            f"Fashion style: {fashion_style}",
            f"Spirit style: {spirit_style}",
            "Recent conversation:",
            *history_lines,
            f"User: {user_message}",
        ]
    )


def _fallback_reply(role: str, input_profile: dict) -> str:
    if role == "guardian":
        return '"..." （守护灵轻轻环绕了你一圈）'
    return '"..." （沉默三秒，然后微微点头）'


def generate_character_reply(
    *,
    payload: dict,
    logger,
    request_id: str | None,
    llm_callable: Callable[[str], str] | None = None,
) -> dict:
    validate_chat_payload(payload)
    prompt = build_chat_prompt(
        input_profile=payload["input_profile"],
        role=payload["role"],
        user_message=payload["message"].strip(),
        recent_messages=payload.get("recent_messages", []),
    )

    llm_callable = llm_callable or DeepSeekClient().generate_text

    try:
        reply = llm_callable(prompt)
        return {
            "reply": reply.strip(),
            "fallback_used": False,
            "role": payload["role"],
        }
    except Exception as exc:
        log_structured_event(
            logger,
            "warning",
            "chat_fallback",
            request_id=request_id,
            task_id=None,
            error=str(exc),
            role=payload["role"],
        )
        return {
            "reply": _fallback_reply(payload["role"], payload["input_profile"]),
            "fallback_used": True,
            "role": payload["role"],
        }
