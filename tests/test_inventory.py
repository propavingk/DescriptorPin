"""Tests for inventory parsing."""

import unittest

from descriptorpin.inventory import InventoryError, parse_inventory


def _minimal():
    return {
        "servers": [
            {
                "name": "s1",
                "transport": "http",
                "tools": [
                    {"name": "t1", "description": "d", "input_schema": {"type": "object"}}
                ],
            }
        ]
    }


class InventoryTest(unittest.TestCase):
    def test_parse_minimal(self):
        inv = parse_inventory(_minimal())
        self.assertEqual(len(inv.servers), 1)
        self.assertEqual(len(inv.all_tools()), 1)
        self.assertEqual(inv.servers[0].transport, "http")

