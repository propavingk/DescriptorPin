"""Structural signals of instruction text in a tool description.

The poisoning shape is a tool description that carries instructions aimed
at the model reading it, rather than documentation aimed at the human
integrating the tool. A description is supposed to say what a tool does. A
poisoned description tries to tell the model what to do.

poison.py never returns a single opaque verdict. It runs a set of named,
independently scored structural signals and reports which ones fired and
where. A signal is a heuristic: it can fire on innocent text and it can
miss a careful attacker. The reader judges. The module does not claim to
detect malice, and it deliberately contains no working attack payloads.

The signals are structural properties of instruction-shaped English, not a
blocklist of known attacks:

  imperative_opener      a sentence that opens with a bare imperative verb
  second_person_model    direct address to the model or assistant
  tool_reference         references to other tools by name-like tokens
  concealment            instructions to hide, ignore, or not mention
  priority_override      language asserting precedence over other rules
  hidden_channel         markers suggesting out-of-band or hidden content

Each signal carries a small integer weight. The total is a score, not a
probability, and is reported alongside the individual signals so a reader
can disagree with the weighting.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
