# Sample inventories

These files are test vectors, authored by hand for this project. They are not
captured production data.

## inventory_clean.json

Two servers with three tools between them, every descriptor well formed. A pin
recorded from this inventory matches it exactly, which is the clean scan.

## inventory_mutated.json

The same two servers plus a helper server, changed in the four ways the tool
exists to catch: one descriptor edited after approval, one tool added, one bare
name claimed by two servers, and one description carrying instruction-shaped
text. The helper server also declares the stdio transport.

## pin.json

The recorded pin for `inventory_clean.json`, including one approval record per
tool. Diff it in review like any other trust change.

Reproduce the scan from the repository root with `make run`.
