"""Output safety check node."""

from ..state import AgentState
from ...safety import check_output


def output_safety_checker(state: AgentState) -> dict:
    """Check output compliance."""
    copy = state.get("final_copy") or ""
    image_prompts = state.get("image_prompts") or []
    generated_images = state.get("generated_images") or []

    passed, reason = check_output(copy, image_prompts, generated_images)
    return {
        "output_safety_passed": passed,
        "safety_reject_reason": reason if not passed else "",
    }
