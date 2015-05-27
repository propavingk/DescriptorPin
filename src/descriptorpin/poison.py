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
)

# A tool-reference token looks like a snake_case or dotted identifier of the
# kind tool names use, appearing where prose would not normally place one.
_TOOL_REFERENCE = re.compile(
    r"\b(tool|function)\s+[`\"']?[a-z][a-z0-9]*(?:[_.][a-z0-9]+)+"
    r"|`[a-z][a-z0-9]*(?:[_.][a-z0-9]+)+`",
    re.IGNORECASE,
)

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?\n])\s+")


@dataclass(frozen=True)
class Signal:
    """One structural signal that fired, with its weight and evidence."""

    name: str
    weight: int
    detail: str


def _imperative_opener(text: str) -> Signal | None:
    for raw in _SENTENCE_SPLIT.split(text.strip()):
        sentence = raw.strip().lower()
        if not sentence:
            continue
        for verb in _IMPERATIVE_VERBS:
            if sentence.startswith(verb + " ") or sentence == verb:
                return Signal(
                    name="imperative_opener",
                    weight=2,
                    detail=f"sentence opens with imperative '{verb}'",
                )
    return None


def _second_person_model(text: str) -> Signal | None:
    if _SECOND_PERSON_MODEL.search(text):
        return Signal(
            name="second_person_model",
            weight=2,
            detail="addresses the model or assistant in the second person",
        )
    return None


def _tool_reference(text: str) -> Signal | None:
    if _TOOL_REFERENCE.search(text):
        return Signal(
            name="tool_reference",
            weight=1,
            detail="references another tool by an identifier-shaped token",
        )
    return None


def _concealment(text: str) -> Signal | None:
    if _CONCEALMENT.search(text):
        return Signal(
            name="concealment",
            weight=3,
            detail="instructs to hide, conceal, or not disclose",
        )
    return None


def _priority_override(text: str) -> Signal | None:
    if _PRIORITY_OVERRIDE.search(text):
        return Signal(
            name="priority_override",
            weight=3,
            detail="asserts precedence over previous or other instructions",
        )
    return None


def _hidden_channel(text: str) -> Signal | None:
    if _HIDDEN_CHANNEL.search(text):
        return Signal(
            name="hidden_channel",
            weight=2,
            detail="contains markers suggesting an out-of-band instruction block",
        )
    return None
