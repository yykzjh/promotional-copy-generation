"""Copy generation node - enhanced context -> promotional copy."""

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ..state import AgentState
from ...config import settings
from ...context import load_stage_context


def _get_llm():
    return ChatOpenAI(
        base_url=settings.main_model_url,
        api_key=settings.main_model_api_key,
        model=settings.main_model,
    )


def copy_writer(state: AgentState) -> dict:
    """Generate promotional copy from enhanced context."""
    enhanced = state.get("enhanced_context") or state.get("raw_requirements") or ""
    platform = state.get("platform") or "xiaohongshu"
    style = state.get("style") or "natural"

    ctx = load_stage_context("copy_write", platform=platform, style=style)
    template = ctx.get("prompt_template", "").strip()
    if not template:
        template = "Generate promotional copy based on the following requirements:\n\n{enhanced_context}"

    platform_rules = ctx.get("skills_content", "")

    prompt = template.format(
        enhanced_context=enhanced,
        platform_rules=platform_rules,
        platform=platform,
        style=style,
    )

    llm = _get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])
    copy = response.content if hasattr(response, "content") else str(response)

    return {"final_copy": copy, "copy_draft": copy}
