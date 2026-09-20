# FAQ

**Does DescriptorPin contact the MCP server?**
No. It reads inventory files on disk and never opens a socket, which is why
it runs in CI and on an air-gapped machine.

**What counts as a descriptor?**
The tool name, description, and input schema. Those three fields are what a
client shows a person before approval.

**Why not hash the raw bytes?**
Raw bytes move on key order and whitespace. The canonical form in canon.py
folds those differences first, so the hash moves only when a value moves.

**Can it tell that a change is malicious?**
No, and it does not try. MUTATION, SHADOW, POISON, and TRANSPORT are shapes
with names. The report says which shape fired and where; the reader judges.
