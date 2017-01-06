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
