"""Tests for cross-server name collision detection."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.shadow import collisions


def _inv(servers):
    return parse_inventory({"servers": servers})


def _server(name, tool_names):
    return {
        "name": name,
        "transport": "http",
        "tools": [{"name": t, "description": "d", "input_schema": {}} for t in tool_names],
