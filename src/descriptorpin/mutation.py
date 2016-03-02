"""Rug pull detection and a field-level diff.

The rug pull shape is a tool that was approved once, then silently changed
its descriptor afterwards. The client already trusts the tool by name, so a
later change to the description or input schema can redirect behaviour
without any fresh approval.

mutation.py compares a current inventory against a pin file. For each tool
it reports one of:

  matched   the current descriptor hash equals the pinned hash
  mutated   the tool is pinned but its descriptor hash differs
  added     the tool is present now but was not in the pin
  removed   the tool was pinned but is absent now

For a mutated tool it computes a field-level diff so the reader sees which
of name, description, or input_schema changed, not just that something did.
The diff never claims intent. It states which field changed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .canon import canonical_descriptor, descriptor_hash, short_digest
from .inventory import Inventory
from .pin import PinFile

MATCHED = "matched"
MUTATED = "mutated"
ADDED = "added"
REMOVED = "removed"


@dataclass(frozen=True)
class FieldChange:
    """One descriptor field that changed between pin and scan."""

    field: str
    pinned: str
    scanned: str


@dataclass(frozen=True)
class ToolStatus:
    """The comparison result for one tool key."""

    key: str
    status: str
    pinned_digest: str
    scanned_digest: str
    changes: tuple = ()


def _field_repr(value: object) -> str:
    """Render a field value for the diff. Schemas become compact JSON."""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def diff_descriptors(pinned_desc: dict, scanned_desc: dict) -> tuple:
    """Return the tuple of FieldChange between two canonical descriptors."""
    a = canonical_descriptor(pinned_desc)
    b = canonical_descriptor(scanned_desc)
    changes = []
    for field_name in ("name", "description", "input_schema"):
        if a[field_name] != b[field_name]:
            changes.append(
                FieldChange(
                    field=field_name,
                    pinned=_field_repr(a[field_name]),
                    scanned=_field_repr(b[field_name]),
                )
            )
    return tuple(changes)


def compare(pin: PinFile, inventory: Inventory) -> list:
    """Compare a scanned inventory against a pin, one ToolStatus per key.

    Results are sorted by key so output is deterministic. A mutated tool
    carries a field-level diff, which requires the current descriptor; the
    diff is computed from the live inventory tool matched by key.
    """
    pinned_by_key = pin.by_key()
    scanned_by_key = {}
    scanned_desc_by_key = {}
    for tool in inventory.all_tools():
        key = inventory.tool_key(tool)
        scanned_by_key[key] = descriptor_hash(tool.descriptor())
        scanned_desc_by_key[key] = tool.descriptor()

    results = []
    all_keys = set(pinned_by_key) | set(scanned_by_key)
    for key in sorted(all_keys):
        in_pin = key in pinned_by_key
        in_scan = key in scanned_by_key
        if in_pin and in_scan:
            pinned_hash = pinned_by_key[key].hash
            scanned_hash = scanned_by_key[key]
            if pinned_hash == scanned_hash:
                results.append(
                    ToolStatus(
                        key=key,
                        status=MATCHED,
                        pinned_digest=short_digest(pinned_hash),
                        scanned_digest=short_digest(scanned_hash),
                    )
                )
            else:
                # A mutated tool: compute the field-level diff between the
                # descriptor stored in the pin and the descriptor seen now.
                # The pin retains the canonical descriptor precisely so this
                # diff names the changed field and shows both values, rather
                # than only reporting that the hash moved.
                pinned_tool = pinned_by_key[key]
                changes = diff_descriptors(
                    pinned_tool.descriptor, scanned_desc_by_key[key]
                )
                results.append(
                    ToolStatus(
                        key=key,
                        status=MUTATED,
                        pinned_digest=short_digest(pinned_hash),
                        scanned_digest=short_digest(scanned_hash),
                        changes=changes,
                    )
                )
        elif in_scan and not in_pin:
            results.append(
                ToolStatus(
                    key=key,
                    status=ADDED,
                    pinned_digest="",
                    scanned_digest=short_digest(scanned_by_key[key]),
                )
            )
        else:
            results.append(
                ToolStatus(
                    key=key,
                    status=REMOVED,
                    pinned_digest=short_digest(pinned_by_key[key].hash),
                    scanned_digest="",
                )
            )
    return results


def mutations(statuses: list) -> list:
    """Filter a comparison to the mutated tools only."""
