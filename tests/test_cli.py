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
        code, out = _run(["scan", CLEAN, "-p", PIN])
        self.assertEqual(code, 0)
        self.assertIn("0 findings", out)

    def test_scan_mutated_exits_one(self):
        code, out = _run(["scan", MUTATED, "-p", PIN])
        self.assertEqual(code, 1)

    def test_scan_reports_every_class(self):
        _, out = _run(["scan", MUTATED, "-p", PIN])
        self.assertIn("MUTATION", out)
        self.assertIn("SHADOW", out)
        self.assertIn("POISON", out)
        self.assertIn("TRANSPORT", out)

    def test_diff_only_reports_mutations(self):
        code, out = _run(["diff", MUTATED, "-p", PIN])
        self.assertEqual(code, 1)
        self.assertIn("MUTATION", out)
        self.assertNotIn("SHADOW", out)

    def test_shadow_only_reports_collisions(self):
        code, out = _run(["shadow", MUTATED])
        self.assertEqual(code, 1)
        self.assertIn("SHADOW", out)
        self.assertNotIn("MUTATION", out)

    def test_pin_then_scan_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_pin = os.path.join(tmp, "pin.json")
            code, _ = _run(["pin", CLEAN, "-o", out_pin])
            self.assertEqual(code, 0)
            code, out = _run(["scan", CLEAN, "-p", out_pin])
            self.assertEqual(code, 0)
            self.assertIn("0 findings", out)

    def test_bad_inventory_is_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.json")
            with open(bad, "w", encoding="utf-8") as handle:
                handle.write("{not json")
            code, _ = _run(["shadow", bad])
            self.assertEqual(code, 2)


if __name__ == "__main__":
