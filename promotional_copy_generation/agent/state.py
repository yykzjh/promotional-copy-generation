"""Agent state definition - simplified multimodal flow."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """Agent graph state."""

    # Input
    raw_requirements: str
    raw_description: str
    input_images: list[bytes]
    platform: str
    style: str

    # Intermediate results
    enhanced_context: str
    copy_draft: str
    image_prompts: list[str]

    # Output
    final_copy: str
    generated_images: list[bytes]

    # Control
    has_input_images: bool
    need_image_generation: bool
    image_count: int
    messages: Annotated[list, add_messages]

    # Safety check
    input_safety_passed: bool
    output_safety_passed: bool
    safety_reject_reason: str
