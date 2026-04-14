import json
from pathlib import Path
from typing import Any, Callable

from backend.prompt.schema import PromptOutput


TEMPLATE_PATH = Path(__file__).parent / "templates" / "prompt_template.txt"


def build_prompt(input_profile: dict) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    style_profile = input_profile.get("style_profile") or {}
    extra_payload = input_profile.get("extra_payload") or {}
    fashion_style = style_profile.get("fashion_style") or input_profile.get(
        "fashion_style"
    ) or "unspecified outfit style"
    spirit_style = style_profile.get("spirit_style") or input_profile.get(
        "spirit_style"
    ) or "unspecified spirit style"

    return template.format(
        display_name=input_profile.get("display_name", ""),
        gender=input_profile.get("gender", ""),
        birth_location=input_profile.get("birth_location", ""),
        birth_datetime=input_profile.get("birth_datetime", ""),
        image_reference=input_profile.get("reference_image_url", ""),
        fashion_style=fashion_style,
        spirit_style=spirit_style,
        personality_tags=", ".join(extra_payload.get("personality_tags", [])),
        scene_preference=extra_payload.get("scene_preference", ""),
        free_text=extra_payload.get("free_text", ""),
    )


def generate_prompt_output(
    input_profile: dict, llm_callable: Callable[[str], str | dict[str, Any]]
) -> PromptOutput:
    prompt = build_prompt(input_profile)
    raw_response = llm_callable(prompt)
    if isinstance(raw_response, dict):
        return PromptOutput.model_validate(raw_response)
    return PromptOutput.model_validate(json.loads(raw_response))
