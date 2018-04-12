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

