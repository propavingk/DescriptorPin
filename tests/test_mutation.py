"""Tests for rug pull mutation detection and the field-level diff."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.mutation import ADDED, MATCHED, MUTATED, REMOVED, compare, mutations
from descriptorpin.pin import build_pin


def _inv(description="original", extra=None):
    tools = [{"name": "t", "description": description, "input_schema": {"type": "object"}}]
    if extra:
        tools.append(extra)
    return parse_inventory(
        {"servers": [{"name": "s", "transport": "http", "tools": tools}]}
    )


class MutationTest(unittest.TestCase):
    def test_unchanged_is_matched(self):
        pin = build_pin(_inv())
        statuses = compare(pin, _inv())
        self.assertEqual(statuses[0].status, MATCHED)
        self.assertEqual(mutations(statuses), [])

    def test_changed_description_is_mutated(self):
        pin = build_pin(_inv("original"))
        statuses = compare(pin, _inv("changed after approval"))
        muts = mutations(statuses)
        self.assertEqual(len(muts), 1)
        self.assertEqual(muts[0].status, MUTATED)

    def test_field_diff_names_the_field(self):
        pin = build_pin(_inv("original"))
        statuses = compare(pin, _inv("changed"))
        change = mutations(statuses)[0].changes
        fields = [c.field for c in change]
        self.assertIn("description", fields)
        self.assertNotIn("name", fields)

    def test_field_diff_shows_both_values(self):
        pin = build_pin(_inv("original"))
        statuses = compare(pin, _inv("changed"))
        change = mutations(statuses)[0].changes[0]
        self.assertEqual(change.pinned, "original")
        self.assertEqual(change.scanned, "changed")

    def test_added_tool(self):
        pin = build_pin(_inv())
        extra = {"name": "new", "description": "d", "input_schema": {}}
        statuses = compare(pin, _inv(extra=extra))
        added = [s for s in statuses if s.status == ADDED]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].key, "s/new")

    def test_removed_tool(self):
        extra = {"name": "gone", "description": "d", "input_schema": {}}
        pin = build_pin(_inv(extra=extra))
        statuses = compare(pin, _inv())
        removed = [s for s in statuses if s.status == REMOVED]
        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0].key, "s/gone")


if __name__ == "__main__":
    unittest.main()
