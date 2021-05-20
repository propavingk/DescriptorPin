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
