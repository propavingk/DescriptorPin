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

