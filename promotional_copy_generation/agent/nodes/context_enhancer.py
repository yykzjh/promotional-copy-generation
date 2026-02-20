"""Context enhancement node - outputs enhanced prompt and need_image_generation in one LLM call."""

import json
import re

from langchain_openai import ChatOpenAI

from ..state import AgentState
from ..multimodal import build_human_message
from ...config import settings
from ...context import load_stage_context


def _get_llm(has_images: bool):
    if has_images:
        return ChatOpenAI(
            base_url=settings.vlm_text_gen_url,
            api_key=settings.vlm_text_gen_resolved_api_key,
            model=settings.vlm_text_gen_resolved_model,
        )
    return ChatOpenAI(
        base_url=settings.main_model_url,
        api_key=settings.main_model_api_key,
        model=settings.main_model,
    )


def _parse_response(content: str) -> tuple[str, bool, int]:
    """Parse LLM response for enhanced context, need_images, and image_count."""
    enhanced = content.strip()
    need_images = False
    image_count = 1

    for match in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content):
        try:
            data = json.loads(match.group())
            if "enhanced" in data:
                enhanced = str(data["enhanced"]).strip()
            if "need_images" in data:
                need_images = bool(data["need_images"])
            if "image_count" in data:
                n = data["image_count"]
                if isinstance(n, (int, float)):
                    image_count = max(1, min(4, int(n)))
            break
        except json.JSONDecodeError:
            continue
    return enhanced, need_images, image_count


def context_enhancer(state: AgentState) -> dict:
    """
    Convert vague description to clear, structured requirements.
    Also outputs need_image_generation from LLM: with input images usually true,
    unless user explicitly/implicitly indicates text-only; without images, LLM decides.
    Single LLM call for both enhanced context and image decision.
    """
    requirements = state.get("raw_requirements") or ""
    description = state.get("raw_description") or ""
    images = state.get("input_images") or []
    has_images = state.get("has_input_images", False) and images

    ctx = load_stage_context("context_enhance")
    template = ctx.get("prompt_template", "").strip()
    if not template:
        template = (
            "Structure and clarify the following requirements:\n\n{input}\n\n"
            "Output JSON: {{\"enhanced\": \"...\", \"need_images\": true/false, "
            "\"image_count\": 1-4 (when need_images=true), \"reason\": \"...\"}}"
        )

    input_text = f"Requirements: {requirements}\n\nDetailed description: {description}".strip()
    if has_images:
        input_text += "\n\n[The user has uploaded images. Analyze them and incorporate visual context into the enhanced requirements.]"

    prompt = template.format(input=input_text)

    msg = build_human_message(prompt, images if has_images else None)
    llm = _get_llm(has_images)
    response = llm.invoke([msg])
    content = response.content if hasattr(response, "content") else str(response)

    enhanced, need_image_generation, image_count = _parse_response(content)

    return {
        "enhanced_context": enhanced or requirements,
        "need_image_generation": need_image_generation,
        "image_count": image_count if need_image_generation else 0,
    }
