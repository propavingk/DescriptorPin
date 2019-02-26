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
        }
    )


class TransportTest(unittest.TestCase):
    def test_stdio_is_flagged(self):
        findings = assess(_inv(["stdio"]))
        self.assertTrue(findings[0].flagged)

    def test_http_not_flagged(self):
