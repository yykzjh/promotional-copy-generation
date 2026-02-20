"""MCP tool registry - stage-to-tools mapping, config-driven and extensible."""

import logging
from typing import Any

import yaml

from ..config import settings
from .config import get_server_configs

logger = logging.getLogger(__name__)


def _load_stage_contexts() -> dict[str, Any]:
    path = settings.stage_contexts_path
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def get_tool_names_for_stage(stage: str) -> list[str]:
    """
    Get MCP tool names for a stage.
    Sources (in order):
      1. stage_contexts.yaml: stages.<stage>.mcp_tools
      2. mcp_servers.yaml: servers with tools_filter, merged by stage
    """
    stage_config = _load_stage_contexts()
    stages = stage_config.get("stages", {})
    cfg = stages.get(stage, {})

    # Primary: explicit mcp_tools in stage config
    mcp_tools = cfg.get("mcp_tools")
    if mcp_tools is not None:
        return list(mcp_tools) if isinstance(mcp_tools, list) else []

    # Fallback: global stage_tools mapping in mcp config
    mcp_config_path = settings.mcp_servers_path
    if mcp_config_path.exists():
        raw = yaml.safe_load(mcp_config_path.read_text(encoding="utf-8")) or {}
        stage_tools = raw.get("stage_tools", {})
        return stage_tools.get(stage, [])

    return []


def get_all_available_tool_names() -> set[str]:
    """Get all tool names from configured servers (tools_filter or all)."""
    configs = get_server_configs()
    names: set[str] = set()
    for cfg in configs.values():
        filter_list = cfg.get("tools_filter")
        if filter_list:
            names.update(filter_list)
        # If no filter, we don't know names until client connects; skip
    return names


def register_stage_tools(stage: str, tool_names: list[str]) -> None:
    """
    Programmatically register tools for a stage.
    Extensible: custom code can call this to add tools without config.
    """
    # This would require a mutable registry; for now we use config-driven only.
    # Extension point: subclasses or plugins could override get_tool_names_for_stage.
    raise NotImplementedError(
        "Use stage_contexts.yaml stages.<stage>.mcp_tools or "
        "mcp_servers.yaml stage_tools for config-driven mapping"
    )
