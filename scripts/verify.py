#!/usr/bin/env python3
"""Quality gate for descriptorpin.

Runs the mechanical checks distilled from the project's lessons. Standard
library only, no network, no third-party dependency. Run from the project
root:

    python scripts/verify.py

Exit code is 0 when every check passes and 1 when any check fails. One line
is printed per check so the output is readable in a CI log, followed by a
single summary line.

The eight checks, in order:

  1. Every .svg under docs/assets/ parses as XML.
  2. No .svg contains feGaussianBlur, feDropShadow, or feTurbulence.
  3. No XML comment in any .svg contains the illegal `--` sequence.
  4. No tracked text file contains U+2014, `&#8212;`, or `&mdash;`.
  5. README.md contains no pandoc style image attribute block.
  6. README.md contains none of the banned marketing terms.
  7. Every .svg carries a viewBox, role="img", a <title>, and a <desc>.
  8. No two text labels sharing a baseline in any .svg overlap.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
README = ROOT / "README.md"

# File extensions treated as tracked text for the em dash sweep.
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".svg",
    ".json",
    ".toml",
    ".cff",
    ".yml",
    ".yaml",
    ".txt",
    ".cfg",
    ".ini",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
}

# Directories that never carry tracked source and only add noise.
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "build", "dist", ".mypy_cache"}

BANNED_MARKETING = (
    "ai powered",
    "ai-powered",
    "seamless",
    "revolutionary",
    "enterprise-grade",
    "enterprise grade",
    "next generation",
    "next-generation",
    "cutting edge",
    "cutting-edge",
    "blazing fast",
    "production ready",
    "production-ready",
    "battle tested",
    "battle-tested",
    "lightning fast",
    "lightning-fast",
    "robust",
    "powerful",
    "effortless",
)

EM_DASH_FORMS = ("\u2014", "&#8212;", "&mdash;")

# Average glyph advance as a fraction of the font size. Sans and mono differ,
# per the width estimate recorded in LESSONS.md.
EM_SANS = 0.58
EM_MONO = 0.60


def _svg_files() -> list[Path]:
    if not ASSETS.is_dir():
        return []
    return sorted(ASSETS.rglob("*.svg"))


def _tracked_text_files() -> list[Path]:
    out: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_SUFFIXES:
            out.append(path)
    return sorted(out)


def check_svg_parses() -> tuple[bool, str]:
    """1. Every .svg under docs/assets/ parses as XML."""
    svgs = _svg_files()
    for svg in svgs:
        try:
            ET.parse(svg)
        except ET.ParseError as exc:
            return False, f"check 1 svg-parses: FAIL {svg.name} does not parse: {exc}"
    return True, f"check 1 svg-parses: OK ({len(svgs)} svg)"


def check_no_forbidden_filters() -> tuple[bool, str]:
    """2. No .svg contains feGaussianBlur, feDropShadow, or feTurbulence."""
    forbidden = ("feGaussianBlur", "feDropShadow", "feTurbulence")
    for svg in _svg_files():
        text = svg.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                return False, f"check 2 no-filters: FAIL {svg.name} contains {token}"
    return True, "check 2 no-filters: OK"


def check_no_double_hyphen_in_comments() -> tuple[bool, str]:
    """3. No XML comment in any .svg contains the illegal `--` sequence."""
    comment = re.compile(r"<!--(.*?)-->", re.DOTALL)
    for svg in _svg_files():
        text = svg.read_text(encoding="utf-8")
        for body in comment.findall(text):
            if "--" in body:
                return False, (
                    f"check 3 comment-hyphen: FAIL {svg.name} has '--' inside a comment"
                )
    return True, "check 3 comment-hyphen: OK"


def check_no_em_dash() -> tuple[bool, str]:
    """4. No tracked text file contains U+2014, `&#8212;`, or `&mdash;`."""
    self_path = Path(__file__).resolve()
    for path in _tracked_text_files():
        # This checker names the three forms as data; skip its own source so
        # the definition list does not trip the check.
        if path.resolve() == self_path:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for form in EM_DASH_FORMS:
            if form in text:
                rel = path.relative_to(ROOT)
                return False, f"check 4 em-dash: FAIL {rel} contains {form!r}"
    return True, "check 4 em-dash: OK"


def check_no_pandoc_image_attr() -> tuple[bool, str]:
    """5. README.md contains no pandoc style image attribute block."""
    if not README.is_file():
        return False, "check 5 pandoc-attr: FAIL README.md missing"
    text = README.read_text(encoding="utf-8")
    pattern = re.compile(r"\)\{[^}]*(?:width|height)[^}]*\}")
    if pattern.search(text):
        return False, "check 5 pandoc-attr: FAIL README has a pandoc image attribute block"
    return True, "check 5 pandoc-attr: OK"


def check_no_marketing_terms() -> tuple[bool, str]:
    """6. README.md contains none of the banned marketing terms."""
    if not README.is_file():
        return False, "check 6 marketing: FAIL README.md missing"
    lowered = README.read_text(encoding="utf-8").lower()
    for term in BANNED_MARKETING:
        if term in lowered:
            return False, f"check 6 marketing: FAIL README contains '{term}'"
    return True, "check 6 marketing: OK"


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def check_svg_accessibility() -> tuple[bool, str]:
    """7. Every .svg carries a viewBox, role="img", a <title>, and a <desc>."""
    for svg in _svg_files():
        tree = ET.parse(svg)
        root = tree.getroot()
        if root.get("viewBox") is None:
            return False, f"check 7 svg-a11y: FAIL {svg.name} has no viewBox"
        if root.get("role") != "img":
            return False, f"check 7 svg-a11y: FAIL {svg.name} has no role=img"
        locals_ = {_localname(el.tag) for el in root.iter()}
        if "title" not in locals_:
            return False, f"check 7 svg-a11y: FAIL {svg.name} has no <title>"
        if "desc" not in locals_:
            return False, f"check 7 svg-a11y: FAIL {svg.name} has no <desc>"
    return True, "check 7 svg-a11y: OK"


