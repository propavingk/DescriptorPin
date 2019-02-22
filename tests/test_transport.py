"""Tests for transport risk assessment."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.transport import assess, flagged


def _inv(transports):
    return parse_inventory(
        {
            "servers": [
                {"name": f"s{i}", "transport": t, "tools": []}
                for i, t in enumerate(transports)
            ]
