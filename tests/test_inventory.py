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

    def test_tool_key_is_server_qualified(self):
        inv = parse_inventory(_minimal())
        tool = inv.all_tools()[0]
        self.assertEqual(inv.tool_key(tool), "s1/t1")

    def test_camel_case_schema_key_accepted(self):
        data = _minimal()
        data["servers"][0]["tools"][0].pop("input_schema")
        data["servers"][0]["tools"][0]["inputSchema"] = {"type": "string"}
        inv = parse_inventory(data)
        self.assertEqual(inv.all_tools()[0].input_schema, {"type": "string"})

    def test_root_not_object_raises(self):
        with self.assertRaises(InventoryError):
            parse_inventory([])

    def test_missing_servers_raises(self):
        with self.assertRaises(InventoryError):
            parse_inventory({})

    def test_tool_without_name_raises(self):
        data = _minimal()
        data["servers"][0]["tools"][0].pop("name")
        with self.assertRaises(InventoryError):
            parse_inventory(data)

    def test_description_defaults_to_empty(self):
        data = _minimal()
        data["servers"][0]["tools"][0].pop("description")
        inv = parse_inventory(data)
        self.assertEqual(inv.all_tools()[0].description, "")


if __name__ == "__main__":
    unittest.main()
