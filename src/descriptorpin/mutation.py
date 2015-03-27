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


