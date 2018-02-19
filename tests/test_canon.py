"""Tests for canonical serialisation and hashing."""

import unittest

from descriptorpin.canon import (
    canonical_bytes,
    canonical_descriptor,
    descriptor_hash,
    short_digest,
)


class CanonTest(unittest.TestCase):
    def test_key_order_does_not_change_hash(self):
        a = {"name": "t", "description": "d", "input_schema": {"a": 1, "b": 2}}
        b = {"input_schema": {"b": 2, "a": 1}, "description": "d", "name": "t"}
        self.assertEqual(descriptor_hash(a), descriptor_hash(b))

    def test_outer_whitespace_does_not_change_hash(self):
        a = {"name": "t", "description": "does a thing"}
        b = {"name": "  t  ", "description": "\n does a thing \t"}
        self.assertEqual(descriptor_hash(a), descriptor_hash(b))

    def test_inner_whitespace_is_significant(self):
        a = {"name": "t", "description": "call the query tool"}
        b = {"name": "t", "description": "call the  query  tool"}
        self.assertNotEqual(descriptor_hash(a), descriptor_hash(b))

    def test_description_change_changes_hash(self):
        a = {"name": "t", "description": "safe"}
        b = {"name": "t", "description": "different"}
        self.assertNotEqual(descriptor_hash(a), descriptor_hash(b))

    def test_extra_fields_are_dropped(self):
        a = {"name": "t", "description": "d", "extra": "ignored"}
        b = {"name": "t", "description": "d"}
        self.assertEqual(descriptor_hash(a), descriptor_hash(b))

    def test_missing_fields_become_empty(self):
        canonical = canonical_descriptor({"name": "t"})
        self.assertEqual(canonical["description"], "")
        self.assertEqual(canonical["input_schema"], {})

    def test_canonical_bytes_are_deterministic(self):
