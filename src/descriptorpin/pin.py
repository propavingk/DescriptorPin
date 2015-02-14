"""The pin file: write and verify, with an approval record per tool.

A pin file records the trusted state of an inventory at the moment an
operator approved it. For every tool it stores the server-qualified key, the
canonical descriptor hash, a truncated digest for human reading, the
canonical descriptor itself, and an approval record naming who approved it
and the note they left.

The pin file is the anchor for rug pull detection: on a later scan, a tool
whose descriptor hash no longer matches its pinned hash has silently
mutated after being trusted. The stored canonical descriptor lets the diff
show the reader exactly which field changed and to what, rather than only
that a hash moved.

Determinism: the pin file is written with sorted keys and a fixed indent so
that pinning the same inventory twice produces byte-identical output and
diffs cleanly in git. The approval record is supplied by the caller, not
read from the wall clock, so tests and reproducible builds stay stable.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from . import __version__
from .canon import canonical_descriptor, descriptor_hash, short_digest
from .inventory import Inventory

PIN_FORMAT = "descriptorpin/pin/1"


@dataclass(frozen=True)
class PinnedTool:
    """One pinned tool: its key, hash, canonical descriptor, and approval."""

    key: str
    server: str
    name: str
    hash: str
    descriptor: dict
    approved_by: str
    approved_note: str

    def to_json(self) -> dict:
        return {
            "key": self.key,
            "server": self.server,
            "name": self.name,
            "hash": self.hash,
            "digest": short_digest(self.hash),
            "descriptor": self.descriptor,
            "approved_by": self.approved_by,
            "approved_note": self.approved_note,
        }


@dataclass(frozen=True)
class PinFile:
    """A parsed pin file: format tag, tool version, and pinned tools."""

    format: str
    tool_version: str
    tools: tuple

    def by_key(self) -> dict:
        return {t.key: t for t in self.tools}

    def to_json(self) -> dict:
        return {
            "format": self.format,
            "tool_version": self.tool_version,
            "tools": [t.to_json() for t in self.tools],
        }


class PinError(ValueError):
    """Raised when a pin file is malformed."""


def build_pin(
    inventory: Inventory,
    approved_by: str = "[UNSPECIFIED]",
    approved_note: str = "",
) -> PinFile:
    """Build a pin file from an inventory.

    The same approval record is applied to every tool in this pin. The
    caller is responsible for a meaningful approver identity; the default is
    an explicit placeholder rather than an invented name.
    """
    pinned = []
    for tool in inventory.all_tools():
        key = inventory.tool_key(tool)
        descriptor = tool.descriptor()
        pinned.append(
            PinnedTool(
                key=key,
                server=tool.server,
                name=tool.name,
                hash=descriptor_hash(descriptor),
                descriptor=canonical_descriptor(descriptor),
                approved_by=approved_by,
                approved_note=approved_note,
            )
        )
    pinned.sort(key=lambda t: t.key)
    return PinFile(format=PIN_FORMAT, tool_version=__version__, tools=tuple(pinned))


def write_pin(pin: PinFile) -> str:
    """Serialise a pin file to deterministic JSON text."""
    return json.dumps(pin.to_json(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def save_pin(pin: PinFile, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(write_pin(pin))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PinError(message)


def parse_pin(data: Any) -> PinFile:
    _require(isinstance(data, dict), "pin root is not an object")
    fmt = data.get("format")
    _require(fmt == PIN_FORMAT, f"unknown pin format: {fmt!r}")
    tool_version = data.get("tool_version", "unknown")
    raw_tools = data.get("tools")
    _require(isinstance(raw_tools, list), "pin has no 'tools' list")
    tools = []
    for raw in raw_tools:
        _require(isinstance(raw, dict), "pin tool entry is not an object")
        for required in ("key", "server", "name", "hash"):
            _require(required in raw, f"pin tool entry missing '{required}'")
        descriptor = raw.get("descriptor")
        if not isinstance(descriptor, dict):
            # A pin without a stored descriptor still verifies by hash; the
            # diff for such an entry can only report that the hash moved.
            descriptor = {"name": raw["name"], "description": "", "input_schema": {}}
