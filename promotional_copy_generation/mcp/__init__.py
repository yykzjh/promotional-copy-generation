"""
MCP (Model Context Protocol) support - modular framework for Agent tool integration.

Modules:
  - client: MCP client wrapper (lazy init, lifecycle)
  - config: Load mcp_servers.yaml with env expansion
  - registry: Stage-to-tool mapping (config-driven)
  - transports: Transport factory (stdio, http, sse); extensible via register_transport()
  - provider: Main facade - get_tools_for_stage(stage), get_all_mcp_tools()

Usage:
  from promotional_copy_generation.mcp import get_tools_for_stage, get_mcp_client

  tools = get_tools_for_stage("context_enhance")
  client = get_mcp_client()
"""

from .client import get_mcp_client, get_all_tools, reset_mcp_client
from .provider import get_tools_for_stage, get_all_mcp_tools, is_mcp_available
from .transports import register_transport

__all__ = [
    "get_mcp_client",
    "get_all_tools",
    "reset_mcp_client",
    "get_tools_for_stage",
    "get_all_mcp_tools",
    "is_mcp_available",
    "register_transport",
]
