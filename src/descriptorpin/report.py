"""Line-oriented reporting for descriptorpin.

Every report function returns a list of strings, one per line, so the CLI
can join them and callers can compose them. Output is deterministic and
diffs cleanly in git. No wall-clock time or randomness appears in output.

The four finding classes are rendered by dedicated functions so the CLI can
combine them for `scan` or emit one for `diff` and `shadow`. A summary line
counts findings by class.
"""

from __future__ import annotations

from .mutation import MUTATED, ToolStatus
from .poison import PoisonReport
from .shadow import Collision
from .transport import TransportFinding


def render_mutations(statuses: list) -> list:
    """Render mutated tools with their field-level diff."""
    lines = []
    muts = [s for s in statuses if s.status == MUTATED]
    for status in muts:
        lines.append(
            f"MUTATION {status.key}: pinned {status.pinned_digest} "
            f"scanned {status.scanned_digest}"
        )
        for change in status.changes:
            lines.append(f"  field {change.field} changed")
            lines.append(f"    pinned:  {_clip(change.pinned)}")
            lines.append(f"    scanned: {_clip(change.scanned)}")
    return lines


def render_added_removed(statuses: list) -> list:
    """Render tools present now but not pinned, and pinned but now absent."""
    lines = []
    for status in statuses:
        if status.status == "added":
            lines.append(f"ADDED {status.key}: scanned {status.scanned_digest}, not in pin")
