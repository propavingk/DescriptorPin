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

