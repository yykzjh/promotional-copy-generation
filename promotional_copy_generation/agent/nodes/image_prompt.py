"""Image prompt generation - requirements (text) + images (optional) -> image description prompts."""

import json

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


def image_prompt_generator(state: AgentState) -> dict:
    """
    Generate image prompts from user requirements and optional input images.
    - text+image: requirements + images when has_input_images
    - text-only: requirements when no input images
    """
    requirements = state.get("raw_requirements") or ""
    description = state.get("raw_description") or ""
    enhanced = state.get("enhanced_context") or ""
    images = state.get("input_images") or []
    has_images = state.get("has_input_images", False) and images

    ctx = load_stage_context("image_prompt")
    template = ctx.get("prompt_template", "").strip()
    skills = ctx.get("skills_content", "")
    if not template:
        template = (
            "Generate image prompts for promotional visuals based on the requirements:\n"
            "{requirements}\n\nGuidelines: {image_prompt_skills}"
        )

    image_count = state.get("image_count") or 1
    image_count = max(1, min(4, int(image_count)))

    prompt = template.format(
        requirements=requirements,
        description=description,
        enhanced_context=enhanced,
        image_prompt_skills=skills,
        image_count=image_count,
    )
    if has_images:
        prompt += "\n\n[The user has provided reference images. Generate prompts that align with their style/content for image generation.]"

    msg = build_human_message(prompt, images if has_images else None)
    llm = _get_llm(has_images)
    response = llm.invoke([msg])
    content = response.content if hasattr(response, "content") else str(response)

    prompts = [content.strip()]
    if "[" in content and "]" in content:
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                prompts = [str(p) for p in parsed if p]
        except Exception:
            pass

    return {"image_prompts": prompts[:image_count]}
