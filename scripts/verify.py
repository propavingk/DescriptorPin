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

