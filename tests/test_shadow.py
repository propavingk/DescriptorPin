"""Tests for cross-server name collision detection."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.shadow import collisions


def _inv(servers):
    return parse_inventory({"servers": servers})

