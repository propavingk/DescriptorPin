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
    render_shadows,
    render_transports,
    summary_line,
)
from .shadow import collisions
from .transport import assess

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="descriptorpin",
        description="Defensive integrity monitor for MCP tool descriptors.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pin = sub.add_parser("pin", help="write a pin file from an inventory")
    p_pin.add_argument("inventory", help="path to the inventory JSON file")
    p_pin.add_argument("-o", "--out", required=True, help="path to write the pin file")
    p_pin.add_argument(
        "--approved-by",
        default="[UNSPECIFIED]",
        help="approver identity recorded per tool",
    )
    p_pin.add_argument("--note", default="", help="approval note recorded per tool")

    p_scan = sub.add_parser("scan", help="report all finding classes")
    p_scan.add_argument("inventory", help="path to the current inventory JSON file")
    p_scan.add_argument("-p", "--pin", required=True, help="path to the pin file")

    p_diff = sub.add_parser("diff", help="report rug pull mutations only")
    p_diff.add_argument("inventory", help="path to the current inventory JSON file")
    p_diff.add_argument("-p", "--pin", required=True, help="path to the pin file")

    p_shadow = sub.add_parser("shadow", help="report cross-server name collisions only")
    p_shadow.add_argument("inventory", help="path to the inventory JSON file")

    sub.add_parser("version", help="print the version")
    return parser


def _cmd_pin(args) -> int:
    inventory = load_inventory(args.inventory)
    pin = build_pin(inventory, approved_by=args.approved_by, approved_note=args.note)
    save_pin(pin, args.out)
    print(f"pinned {len(pin.tools)} tools to {args.out}")
    return EXIT_CLEAN


def _cmd_scan(args) -> int:
    pin = load_pin(args.pin)
    inventory = load_inventory(args.inventory)

    statuses = compare(pin, inventory)
    shadow_items = collisions(inventory)
    poison_named = [
        (inventory.tool_key(t), analyse(t.description)) for t in inventory.all_tools()
    ]
    poison_named = [(k, r) for k, r in poison_named if r.fired]
    transports = assess(inventory)

    lines = []
    lines += render_mutations(statuses)
    lines += render_added_removed(statuses)
    lines += render_shadows(shadow_items)
    lines += render_poison(poison_named)
    lines += render_transports(transports)

    mutation_count = sum(1 for s in statuses if s.status == MUTATED)
    transport_flagged = sum(1 for t in transports if t.flagged)
    for line in lines:
        print(line)
    print(
        summary_line(
            mutation_count,
            len(shadow_items),
            len(poison_named),
            transport_flagged,
