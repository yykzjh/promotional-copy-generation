"""MCP transport factory - extensible transport registration."""

from typing import Any, Callable, Protocol

# Type for add_server-like call: (client, name, config) -> None
AddServerFn = Callable[[Any, str, dict[str, Any]], None]

_transport_registry: dict[str, AddServerFn] = {}


def register_transport(transport_type: str, handler: AddServerFn) -> None:
    """Register a transport handler. Extensible for custom transports."""
    _transport_registry[transport_type] = handler


def _add_stdio(client: Any, name: str, cfg: dict[str, Any]) -> None:
    client.add_server(
        name,
        transport="stdio",
        command=cfg.get("command", "npx"),
        args=cfg.get("args", []),
        env=cfg.get("env") or {},
    )


def _add_http(client: Any, name: str, cfg: dict[str, Any]) -> None:
    client.add_server(
        name,
        transport="http",
        url=cfg.get("url", ""),
        headers=cfg.get("headers"),
    )


def _add_sse(client: Any, name: str, cfg: dict[str, Any]) -> None:
    client.add_server(
        name,
        transport="sse",
        url=cfg.get("url", ""),
        headers=cfg.get("headers"),
    )


# Register built-in transports
register_transport("stdio", _add_stdio)
register_transport("http", _add_http)
register_transport("sse", _add_sse)


def add_server_to_client(client: Any, name: str, cfg: dict[str, Any]) -> None:
    """Add a server to client using registered transport handler."""
    transport = cfg.get("transport", "stdio")
    handler = _transport_registry.get(transport)
    if handler is None:
        raise ValueError(f"Unknown MCP transport: {transport}")
    handler(client, name, cfg)
