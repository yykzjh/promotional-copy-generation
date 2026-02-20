"""Stage context loader - loads from YAML and prompt templates."""

from pathlib import Path
from typing import Any

import yaml

from ..config import settings
from ..skills import get_skills_for_stage


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def get_stage_config(stage: str) -> dict[str, Any]:
    """Get configuration for a stage."""
    config = _load_yaml(settings.stage_contexts_path)
    stages = config.get("stages", {})
    return stages.get(stage, {})


def load_prompt_template(template_path: str) -> str:
    """Load prompt template content."""
    path = settings.config_path / template_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_stage_context(
    stage: str,
    platform: str | None = None,
    style: str | None = None,
) -> dict[str, Any]:
    """Load full stage context (config + Skills + MCP tools)."""
    cfg = get_stage_config(stage)
    skills = get_skills_for_stage(stage)
    skills_content = "\n\n".join(s.content for s in skills)

    prompt_template = cfg.get("prompt_template")
    prompt = ""
    if prompt_template:
        prompt = load_prompt_template(prompt_template)

    # Lazy-load MCP tools only when stage has mcp_tools configured
    mcp_tools = cfg.get("mcp_tools")
    tools = []
    if mcp_tools:
        try:
            from ..mcp import get_tools_for_stage
            tools = get_tools_for_stage(stage)
        except Exception:
            pass

    return {
        "config": cfg,
        "prompt_template": prompt,
        "skills_content": skills_content,
        "skills": skills,
        "mcp_tools": tools,
        "platform": platform,
        "style": style,
    }
