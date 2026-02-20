"""MCP client wrapper - lazy init, lifecycle, graceful degradation."""

import logging
from typing import TYPE_CHECKING, Any

from .config import get_server_configs
from .transports import add_server_to_client

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

_client: Any = None


def get_mcp_client() -> Any | None:
    """Get MCP client (lazy load). Returns None if langchain-mcp-adapters not installed."""
    global _client
    if _client is not None:
        return _client

    try:
        from langchain_mcp_adapters import MultiServerMCPClient
    except ImportError:
        logger.debug("langchain-mcp-adapters not installed; MCP tools disabled")
        return None

    configs = get_server_configs()
    if not configs:
        logger.debug("No MCP servers configured; MCP tools disabled")
        return None

    client = MultiServerMCPClient()
    for name, cfg in configs.items():
        try:
            add_server_to_client(client, name, cfg)
        except Exception as e:
            logger.warning("Failed to add MCP server %s: %s", name, e)

    _client = client
    return _client


def reset_mcp_client() -> None:
    """Reset client (for testing or config reload)."""
    global _client
    _client = None


def get_all_tools(tools_filter: list[str] | None = None) -> list["BaseTool"]:
    """Get all LangChain tools from MCP client. Optionally filter by tool names."""
    client = get_mcp_client()
    if not client:
        return []

    try:
        tools = client.get_langchain_tools()
    except Exception as e:
        logger.warning("Failed to get MCP tools: %s", e)
        return []

    if tools_filter:
        tools = [t for t in tools if t.name in tools_filter]
    return tools
