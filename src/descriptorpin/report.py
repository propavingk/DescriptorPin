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
