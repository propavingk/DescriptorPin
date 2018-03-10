"""Tests for inventory parsing."""

import unittest

from descriptorpin.inventory import InventoryError, parse_inventory


def _minimal():
    return {
        "servers": [
            {
                "name": "s1",
                "transport": "http",
                "tools": [
                    {"name": "t1", "description": "d", "input_schema": {"type": "object"}}
                ],
            }
        ]
    }


