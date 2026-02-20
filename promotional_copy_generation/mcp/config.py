"""MCP configuration loading and schema."""

import os
import re
from pathlib import Path
from typing import Any

import yaml

from ..config import settings


def _expand_env_vars(value: Any) -> Any:
    """Expand ${VAR} and $VAR in strings; recurse into dicts/lists."""
    if isinstance(value, str):
        # Replace ${VAR} or $VAR with env value
        def replacer(m: re.Match[str]) -> str:
            var = m.group(1) or m.group(2)
            return os.environ.get(var, m.group(0))

        return re.sub(r"\$\{([^}]+)\}|\$(\w+)", replacer, value)
    if isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env_vars(v) for v in value]
    return value


def load_mcp_config() -> dict[str, Any]:
    """Load mcp_servers.yaml with env var expansion."""
    path = settings.mcp_servers_path
    if not path.exists():
        return {"servers": {}}
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return _expand_env_vars(raw)


def get_server_configs() -> dict[str, dict[str, Any]]:
    """Get enabled server configs: {server_name: config}."""
    config = load_mcp_config()
    servers = config.get("servers", {})
    return {
        name: cfg
        for name, cfg in servers.items()
        if cfg.get("enabled", True)
    }
