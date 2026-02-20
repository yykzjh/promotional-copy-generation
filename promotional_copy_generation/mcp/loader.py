"""
MCP loader - backward-compatible facade.

Delegates to provider. Prefer using mcp.provider or mcp directly.
"""

from .provider import get_tools_for_stage
from .client import get_mcp_client

__all__ = ["get_mcp_client", "get_tools_for_stage"]
