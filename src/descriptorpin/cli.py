"""Command line interface for descriptorpin.

Subcommands:

  pin      read an inventory, write a pin file recording trusted state
  scan     read a pin and a current inventory, report every finding class
  diff     report only rug pull mutations between a pin and an inventory
  shadow   report only cross-server name collisions in an inventory
  version  print the version

Exit codes:
  0  clean, no findings
  1  findings present
  2  usage or input error
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .inventory import InventoryError, load_inventory
from .mutation import MUTATED, compare
from .pin import PinError, build_pin, load_pin, save_pin
from .poison import analyse
from .report import (
    render_added_removed,
    render_mutations,
    render_poison,
