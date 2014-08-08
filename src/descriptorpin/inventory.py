"""Parse a server and tool inventory.

An inventory is a JSON document describing the MCP servers a client is
configured to talk to, and the tools each server exposes. descriptorpin
reads an inventory both when pinning (recording the trusted state) and when
scanning (checking the current state against the pin).

The parser is strict about structure and forgiving about optional fields.
It raises InventoryError with a specific message rather than letting a
KeyError or TypeError escape, so the CLI can print a usage-grade message
and exit 2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


class InventoryError(ValueError):
    """Raised when an inventory document is malformed."""


@dataclass(frozen=True)
class Tool:
    """One tool descriptor as declared by a server."""

    name: str
    description: str
    input_schema: dict
    server: str

    def descriptor(self) -> dict:
        """Return the three pinned fields as a plain mapping."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass(frozen=True)
class Server:
    """One MCP server and the tools it exposes."""

    name: str
    transport: str
    tools: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class Inventory:
    """A parsed inventory: an ordered collection of servers."""

    servers: tuple = field(default_factory=tuple)

    def all_tools(self) -> list:
        """Flatten every tool across every server, preserving order."""
        out: list = []
        for server in self.servers:
            out.extend(server.tools)
        return out

    def tool_key(self, tool: Tool) -> str:
        """The pin key for a tool: server-qualified name."""
        return f"{tool.server}/{tool.name}"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def _parse_tool(raw: Any, server_name: str) -> Tool:
    _require(isinstance(raw, dict), f"tool in server '{server_name}' is not an object")
    name = raw.get("name")
    _require(isinstance(name, str) and name != "", f"tool in server '{server_name}' has no name")
    description = raw.get("description", "")
    _require(isinstance(description, str), f"tool '{name}' description is not a string")
    schema = raw.get("input_schema", raw.get("inputSchema", {}))
    _require(isinstance(schema, dict), f"tool '{name}' input_schema is not an object")
    return Tool(name=name, description=description, input_schema=schema, server=server_name)


def _parse_server(raw: Any) -> Server:
    _require(isinstance(raw, dict), "server entry is not an object")
    name = raw.get("name")
    _require(isinstance(name, str) and name != "", "server has no name")
    transport = raw.get("transport", "unknown")
    _require(isinstance(transport, str), f"server '{name}' transport is not a string")
    raw_tools = raw.get("tools", [])
    _require(isinstance(raw_tools, list), f"server '{name}' tools is not a list")
    tools = tuple(_parse_tool(t, name) for t in raw_tools)
    return Server(name=name, transport=transport, tools=tools)


def parse_inventory(data: Any) -> Inventory:
    """Parse a decoded JSON inventory document into an Inventory."""
    _require(isinstance(data, dict), "inventory root is not an object")
