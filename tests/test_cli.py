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
