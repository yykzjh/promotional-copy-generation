"""Image generation node - text-to-image only."""

import base64
from typing import Any

import httpx

from ..state import AgentState
from ...config import settings
from ...context import load_stage_context


def _call_image_gen_api(prompt: str, n: int = 1) -> list[bytes]:
    """
    Call image generation API (text-to-image).
    API format follows OpenAI /v1/images/generations; adapt per backend.
    n: number of images to generate from the prompt.
    """
    base = settings.image_gen_url.rstrip("/")
    if base.endswith("/v1"):
        endpoint = f"{base}/images/generations"
    elif "/v1" in base:
        endpoint = f"{base}/images/generations"
    else:
        endpoint = f"{base}/v1/images/generations"

    model = settings.image_gen_model  # VLM_IMAGE_GEN_MODEL or LLM_MAIN_MODEL

    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "size": settings.image_gen_size,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                endpoint,
                json=body,
                headers={
                    "Authorization": f"Bearer {settings.image_gen_api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return []

    # Parse response - support common formats
    images: list[bytes] = []
    if "data" in data:
        for item in data["data"]:
            b64 = item.get("b64_json") or item.get("url", "")
            if b64:
                if b64.startswith("data:"):
                    b64 = b64.split(",", 1)[-1]
                try:
                    images.append(base64.b64decode(b64))
                except Exception:
                    pass
    return images


def _build_prompts_block(prompts: list[str]) -> str:
    """Join prompts with blank lines, each prefixed with index."""
    parts = []
    for i, p in enumerate(prompts):
        parts.append(f"第 {i + 1} 张图像的描述：\n{p.strip()}")
    return "\n\n".join(parts)


def image_generator(state: AgentState) -> dict:
    """
    Generate promotional images from prompts (text-to-image only).
    All prompts are filled into the template and one API call is made with n=image_count.
    """
    if not settings.image_gen_enabled:
        return {"generated_images": []}

    prompts = state.get("image_prompts") or []
    if not prompts:
        return {"generated_images": []}

    image_count = max(1, min(4, state.get("image_count") or len(prompts)))
    prompts = prompts[:image_count]

    ctx = load_stage_context("image_gen")
    raw = ctx.get("prompt_template", "").strip()
    template = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("#")).strip()

    prompts_block = _build_prompts_block(prompts)
    final_prompt = template.format(image_count=image_count, prompts=prompts_block).strip()

    imgs = _call_image_gen_api(final_prompt, n=image_count)
    return {"generated_images": imgs}
