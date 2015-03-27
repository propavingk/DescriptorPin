"""Rug pull detection and a field-level diff.

The rug pull shape is a tool that was approved once, then silently changed
its descriptor afterwards. The client already trusts the tool by name, so a
later change to the description or input schema can redirect behaviour
without any fresh approval.

mutation.py compares a current inventory against a pin file. For each tool
it reports one of:

  matched   the current descriptor hash equals the pinned hash
  mutated   the tool is pinned but its descriptor hash differs
  added     the tool is present now but was not in the pin
  removed   the tool was pinned but is absent now

