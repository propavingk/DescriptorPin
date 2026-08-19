"""Contract tests for the CLI surface that consumers depend on."""

import re
import unittest

from descriptorpin import __version__


class TestVersionContract(unittest.TestCase):
    def test_version_is_semver(self):
        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")

    def test_version_has_three_parts(self):
        self.assertEqual(len(__version__.split(".")), 3)


if __name__ == "__main__":
    unittest.main()
