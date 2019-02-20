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
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].name, "query")
        self.assertEqual(found[0].count, 2)
        self.assertEqual(found[0].servers, ("s1", "s2"))

    def test_same_name_on_one_server_is_not_a_collision(self):
        inv = _inv([_server("s1", ["dup", "dup"])])
        self.assertEqual(collisions(inv), [])

    def test_three_way_collision(self):
        inv = _inv(
            [_server("s1", ["x"]), _server("s2", ["x"]), _server("s3", ["x"])]
