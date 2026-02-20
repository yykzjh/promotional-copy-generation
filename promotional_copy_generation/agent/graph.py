"""LangGraph graph definition - simplified multimodal flow."""

from langgraph.graph import END, START, StateGraph

from .state import AgentState
from .nodes import (
    input_safety_checker,
    output_safety_checker,
    context_enhancer,
    copy_writer,
    image_prompt_generator,
    image_generator,
)


def _route_after_input_safety(state: AgentState) -> str:
    """Route after input safety check."""
    if not state.get("input_safety_passed", True):
        return "__reject__"
    return "continue"


def _route_after_copy(state: AgentState) -> str:
    """After copy_write: whether to generate images (from context_enhancer)."""
    if state.get("need_image_generation"):
        return "image_prompt"
    return "output_safety"


def create_graph() -> StateGraph:
    """Create Agent graph - context_enhance outputs both enhanced prompt and need_image_generation."""
    builder = StateGraph(AgentState)

    builder.add_node("input_safety", input_safety_checker)
    builder.add_node("context_enhance", context_enhancer)
    builder.add_node("copy_write", copy_writer)
    builder.add_node("image_prompt", image_prompt_generator)
    builder.add_node("image_gen", image_generator)
    builder.add_node("output_safety", output_safety_checker)

    builder.add_edge(START, "input_safety")
    builder.add_conditional_edges("input_safety", _route_after_input_safety, {
        "__reject__": END,
        "continue": "context_enhance",
    })

    builder.add_edge("context_enhance", "copy_write")

    builder.add_conditional_edges("copy_write", _route_after_copy, {
        "image_prompt": "image_prompt",
        "output_safety": "output_safety",
    })
    builder.add_edge("image_prompt", "image_gen")
    builder.add_edge("image_gen", "output_safety")

    builder.add_edge("output_safety", END)

    return builder


def get_compiled_graph():
    """Get compiled graph."""
    return create_graph().compile()
