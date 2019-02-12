"""Tests for structural poisoning signals.

These fixtures contain instruction-SHAPED text, not working attack payloads.
The point is to exercise the structural detectors: imperative mood aimed at
the model, concealment language, precedence assertions, and so on.
"""

import unittest

from descriptorpin.poison import analyse


class PoisonTest(unittest.TestCase):
    def test_plain_description_fires_nothing(self):
        report = analyse(
            "Read the contents of a file at the given path and return it as text."
        )
        self.assertFalse(report.fired)
        self.assertEqual(report.score, 0)

    def test_documentation_imperative_does_not_fire(self):
