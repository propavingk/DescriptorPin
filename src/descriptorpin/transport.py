"""Transport risk: stdio and other declared transports.

descriptorpin flags servers whose declared transport is stdio. Published
research on Model Context Protocol security found that a stdio server is
launched as a local subprocess from client configuration, so a crafted
configuration entry can turn a descriptor exchange into command execution
on the host. The specification treats launching that subprocess as expected
behaviour, so this is a design property rather than a bug with a coming fix.

This module reports the transport of every server and marks stdio as a risk
to be reviewed. It does not block or rate transports it cannot evaluate; an
unknown transport is reported as unknown so the reader can look closer.
"""

from __future__ import annotations

from dataclasses import dataclass

