"""Tests for rug pull mutation detection and the field-level diff."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.mutation import ADDED, MATCHED, MUTATED, REMOVED, compare, mutations
from descriptorpin.pin import build_pin


def _inv(description="original", extra=None):
    tools = [{"name": "t", "description": description, "input_schema": {"type": "object"}}]
    if extra:
        tools.append(extra)
