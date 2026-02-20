"""FastAPI routes."""

import base64
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .models import GenerateResponse
from ..agent.graph import get_compiled_graph
from ..agent.state import AgentState
from ..config import settings
from ..skills import load_skills_from_dirs
from ..skills.registry import clear_registry

router = APIRouter(prefix="/api", tags=["generate"])

# Initialize Skills (loaded at application startup)
_builtin = Path(__file__).resolve().parent.parent / "skills" / "builtin"
if _builtin.exists():
    clear_registry()
    load_skills_from_dirs([_builtin] + settings.extra_skills_dirs)


@router.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    requirements: Annotated[str, Form()],
    description: Annotated[str | None, Form()] = None,
    platform: Annotated[str | None, Form()] = None,
    style: Annotated[str | None, Form()] = None,
    images: Annotated[list[UploadFile] | None, File()] = None,
):
    """Generate promotional copy. Image generation is decided dynamically: always if images provided, else by LLM from requirements."""
    input_images: list[bytes] = []
    if images:
        for img in images:
            input_images.append(await img.read())

    initial_state: AgentState = {
        "raw_requirements": requirements,
        "raw_description": description or "",
        "input_images": input_images,
        "platform": platform or "xiaohongshu",
        "style": style or "natural",
        "has_input_images": len(input_images) > 0,
    }

    graph = get_compiled_graph()
    try:
        result = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Input rejected by safety check
    if not result.get("input_safety_passed", True):
        raise HTTPException(
            status_code=400,
            detail=result.get("safety_reject_reason", "Input failed safety check"),
        )

    copy = result.get("final_copy", "")
    if not copy:
        copy = result.get("copy_draft", "")

    image_prompts = result.get("image_prompts")
    generated = result.get("generated_images") or []
    images_b64 = [base64.b64encode(b).decode() for b in generated] if generated else None

    return GenerateResponse(
        copy_text=copy,
        image_prompts=image_prompts,
        generated_images=images_b64,
        metadata={"platform": platform, "style": style},
    )
