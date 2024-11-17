"""Tests for pin build, save, and load round-trip."""

import json
import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.pin import PinError, build_pin, parse_pin, write_pin


def _inv():
    return parse_inventory(
        {
            "servers": [
                {
                    "name": "s1",
                    "transport": "http",
                    "tools": [
                        {"name": "b", "description": "second", "input_schema": {}},
                        {"name": "a", "description": "first", "input_schema": {}},
                    ],
                }
            ]
        }
    )


class PinTest(unittest.TestCase):
    def test_build_pins_every_tool(self):
        pin = build_pin(_inv())
        self.assertEqual(len(pin.tools), 2)

    def test_tools_sorted_by_key(self):
        pin = build_pin(_inv())
        keys = [t.key for t in pin.tools]
        self.assertEqual(keys, sorted(keys))

    def test_approval_record_applied(self):
        pin = build_pin(_inv(), approved_by="[MAINTAINER CONTACT]", approved_note="note")
        for tool in pin.tools:
            self.assertEqual(tool.approved_by, "[MAINTAINER CONTACT]")
            self.assertEqual(tool.approved_note, "note")

    def test_write_is_deterministic(self):
        self.assertEqual(write_pin(build_pin(_inv())), write_pin(build_pin(_inv())))

    def test_round_trip(self):
        pin = build_pin(_inv())
        reparsed = parse_pin(json.loads(write_pin(pin)))
        self.assertEqual(
            [t.hash for t in pin.tools], [t.hash for t in reparsed.tools]
        )

    def test_descriptor_is_stored_for_diff(self):
        pin = build_pin(_inv())
        tool = pin.by_key()["s1/a"]
        self.assertEqual(tool.descriptor["description"], "first")

    def test_bad_format_raises(self):
        with self.assertRaises(PinError):
            parse_pin({"format": "wrong", "tools": []})


if __name__ == "__main__":
    unittest.main()
