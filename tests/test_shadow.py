"""Tests for cross-server name collision detection."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.shadow import collisions


def _inv(servers):
    return parse_inventory({"servers": servers})


def _server(name, tool_names):
    return {
        "name": name,
        "transport": "http",
        "tools": [{"name": t, "description": "d", "input_schema": {}} for t in tool_names],
    }


class ShadowTest(unittest.TestCase):
    def test_no_collision_when_names_unique(self):
        inv = _inv([_server("s1", ["a"]), _server("s2", ["b"])])
        self.assertEqual(collisions(inv), [])

    def test_collision_across_two_servers(self):
        inv = _inv([_server("s1", ["query"]), _server("s2", ["query"])])
        found = collisions(inv)
