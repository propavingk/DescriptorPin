"""Tests for pin build, save, and load round-trip."""

import json
import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.pin import PinError, build_pin, parse_pin, write_pin


def _inv():
    return parse_inventory(
        {
            "servers": [
                {
                    "name": "s1",
                    "transport": "http",
                    "tools": [
                        {"name": "b", "description": "second", "input_schema": {}},
                        {"name": "a", "description": "first", "input_schema": {}},
                    ],
                }
