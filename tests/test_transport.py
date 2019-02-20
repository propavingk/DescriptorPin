"""Tests for transport risk assessment."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.transport import assess, flagged


def _inv(transports):
