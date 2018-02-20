"""End-to-end CLI tests against the authored sample fixtures."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from descriptorpin.cli import main

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(os.path.dirname(HERE), "samples")
CLEAN = os.path.join(SAMPLES, "inventory_clean.json")
MUTATED = os.path.join(SAMPLES, "inventory_mutated.json")
PIN = os.path.join(SAMPLES, "pin.json")


def _run(argv):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(argv)
    return code, buffer.getvalue()


class CliTest(unittest.TestCase):
    def test_version_is_clean(self):
        code, out = _run(["version"])
        self.assertEqual(code, 0)
        self.assertIn("descriptorpin", out)

    def test_scan_clean_exits_zero(self):
