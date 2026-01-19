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
        elif status.status == "removed":
            lines.append(f"REMOVED {status.key}: pinned {status.pinned_digest}, absent now")
    return lines


def render_shadows(items: list) -> list:
    """Render cross-server name collisions."""
    lines = []
    for collision in items:
        servers = ", ".join(collision.servers)
        lines.append(
            f"SHADOW {collision.name}: claimed by {collision.count} servers ({servers})"
        )
        lines.append("  precedence risk: client resolution order decides the winner")
    return lines


def render_poison(named: list) -> list:
    """Render poisoning signals. `named` is a list of (key, PoisonReport)."""
    lines = []
    for key, report in named:
        if not report.fired:
            continue
        lines.append(f"POISON {key}: score {report.score}, {len(report.signals)} signals")
        for signal in report.signals:
            lines.append(f"  signal {signal.name} (weight {signal.weight}): {signal.detail}")
    return lines


def render_transports(findings: list) -> list:
    """Render flagged transports."""
    lines = []
    for finding in findings:
        if finding.flagged:
            lines.append(
                f"TRANSPORT {finding.server}: transport '{finding.transport}' flagged, "
                f"{finding.note}"
            )
    return lines


def summary_line(
    mutation_count: int,
    shadow_count: int,
    poison_count: int,
    transport_count: int,
) -> str:
    """A single deterministic summary counting findings by class."""
    total = mutation_count + shadow_count + poison_count + transport_count
    return (
        f"summary: {total} findings "
        f"({mutation_count} mutation, {shadow_count} shadow, "
        f"{poison_count} poison, {transport_count} transport)"
    )


def _clip(text: str, width: int = 88) -> str:
    """Clip a value for display, marking truncation explicitly."""
    text = text.replace("\n", " ")
    if len(text) <= width:
        return text
    return text[: width - 3] + "..."

# draft note 1713
