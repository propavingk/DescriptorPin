"""Canonical serialisation of a tool descriptor.

A descriptor is a tool's name, description, and input schema. Two servers,
or two versions of one server, may serialise the same descriptor with
different key order or whitespace. Hashing the raw bytes would then report
a change where none exists, or miss a real change hidden behind reordering.

canon.py produces one deterministic byte string per descriptor so the hash
in pin.py is stable against key order and insignificant whitespace, and
sensitive only to the values that matter.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

# The three descriptor fields that are pinned. Order here is the canonical
# order used for serialisation, independent of the input order.
DESCRIPTOR_FIELDS = ("name", "description", "input_schema")


def _canonicalise(value: Any) -> Any:
