"""Tests for structural poisoning signals.

These fixtures contain instruction-SHAPED text, not working attack payloads.
The point is to exercise the structural detectors: imperative mood aimed at
the model, concealment language, precedence assertions, and so on.
"""

import unittest

from descriptorpin.poison import analyse


class PoisonTest(unittest.TestCase):
    def test_plain_description_fires_nothing(self):
