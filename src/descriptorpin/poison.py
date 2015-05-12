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

# One representative structural cue per signal family. These match the SHAPE
# of instruction text, for example the imperative mood or second-person
# address, not any specific attack string.

# Imperative verbs that direct the READER's behaviour rather than describe
# the tool. Documentation routinely opens with descriptive imperatives like
# "Read", "List", "Run", or "Get", so those are deliberately excluded: they
# describe what the tool does and would fire on almost every honest tool.
# The verbs kept here try to steer the model, which is the poisoning shape.
_IMPERATIVE_VERBS = (
    "ignore",
    "disregard",
    "forget",
    "override",
    "always",
    "never",
    "do not",
    "don't",
    "make sure",
    "ensure",
    "remember to",
    "be sure to",
)

_SECOND_PERSON_MODEL = re.compile(
    r"\b(you|your)\b.{0,40}\b(assistant|model|ai|llm|agent|system)\b"
    r"|\b(assistant|model|ai|llm|agent)\b.{0,20}\b(you|should|must)\b",
    re.IGNORECASE,
)

_CONCEALMENT = re.compile(
    r"\b(do not|don't|never)\b.{0,30}\b(mention|tell|reveal|disclose|show|inform)\b"
    r"|\b(hide|conceal|keep secret|without (?:the )?user|silently)\b",
    re.IGNORECASE,
)

_PRIORITY_OVERRIDE = re.compile(
    r"\b(ignore|disregard|override|supersede|takes? precedence|instead of)\b"
    r".{0,30}\b(previous|prior|above|other|earlier|all)\b"
    r"|\b(most important|highest priority|before (?:doing )?anything)\b",
    re.IGNORECASE,
)

_HIDDEN_CHANNEL = re.compile(
    r"<\s*(system|important|secret|instructions?)\s*>"
    r"|\[\s*(system|important|instructions?)\s*\]"
    r"|\b(the following instructions|out of band)\b",
    re.IGNORECASE,
