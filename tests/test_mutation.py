"""Tests for rug pull mutation detection and the field-level diff."""

import unittest

from descriptorpin.inventory import parse_inventory
from descriptorpin.mutation import ADDED, MATCHED, MUTATED, REMOVED, compare, mutations
