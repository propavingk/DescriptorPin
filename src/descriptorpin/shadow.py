"""Cross-server name collision detection and precedence risk.

The shadowing shape is two or more servers exposing a tool with the same
name. A client that resolves a tool by bare name must pick one, and the
losing definition is shadowed. An attacker who registers a second server
with a colliding name can intercept calls the operator believed were going
elsewhere, or can define the tool the client actually binds to.

shadow.py groups tools by bare name across all servers and reports every
name claimed by two or more servers. It states which servers collide and
notes precedence risk: the client's resolution order decides the winner,
and that order is often undocumented, so the collision alone is the finding.

The module does not decide which server is legitimate. It reports the
collision and the servers involved and leaves the judgement to the reader.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .inventory import Inventory


@dataclass(frozen=True)
class Collision:
    """One tool name claimed by more than one server."""

    name: str
    servers: tuple

    @property
    def count(self) -> int:
        return len(self.servers)


def collisions(inventory: Inventory) -> list:
    """Return the sorted list of name collisions across servers.

    A tool name appearing twice on the same server is not a cross-server
    collision, so servers are de-duplicated per name before counting. The
    result is sorted by name for deterministic output.
    """
    by_name = defaultdict(list)
    for tool in inventory.all_tools():
        servers_for_name = by_name[tool.name]
        if tool.server not in servers_for_name:
            servers_for_name.append(tool.server)

    found = []
    for name in sorted(by_name):
        servers = by_name[name]
        if len(servers) >= 2:
            found.append(Collision(name=name, servers=tuple(sorted(servers))))
    return found
