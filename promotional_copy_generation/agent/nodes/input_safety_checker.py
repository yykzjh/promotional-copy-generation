"""Input safety check node."""

from ..state import AgentState
from ...safety import check_input


def input_safety_checker(state: AgentState) -> dict:
    """Check input compliance."""
    requirements = state.get("raw_requirements") or ""
    description = state.get("raw_description") or ""
    images = state.get("input_images") or []

    passed, reason = check_input(requirements, description or None, images or None)
    return {
        "input_safety_passed": passed,
        "safety_reject_reason": reason if not passed else "",
    }
