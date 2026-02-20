"""
MCP tool provider - main facade for Agent integration.

Usage:
    from promotional_copy_generation.mcp import get_tools_for_stage

    tools = get_tools_for_stage("context_enhance")
    # Use tools with LLM/agent
"""

import logging
from typing import TYPE_CHECKING

from .client import get_all_tools
from .registry import get_tool_names_for_stage

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


def get_tools_for_stage(stage: str) -> list["BaseTool"]:
    """
    Get MCP tools available for a graph stage.
    Returns empty list if no tools configured, MCP disabled, or on error.
    """
    tool_names = get_tool_names_for_stage(stage)
    if not tool_names:
        return []

    tools = get_all_tools(tools_filter=tool_names)
    if len(tools) < len(tool_names):
        found = {t.name for t in tools}
        missing = set(tool_names) - found
        logger.debug("MCP tools not found for stage %s: %s", stage, missing)
    return tools


def get_all_mcp_tools() -> list["BaseTool"]:
    """Get all MCP tools (no stage filter). For debugging or custom use."""
    return get_all_tools(tools_filter=None)


def is_mcp_available() -> bool:
    """Check if MCP client is available and has servers configured."""
    from .client import get_mcp_client
    return get_mcp_client() is not None
