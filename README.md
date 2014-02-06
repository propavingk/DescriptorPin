<div align="center">

<img src="docs/assets/logo.svg" width="300"
     alt="DescriptorPin wordmark beside a pinned descriptor card and a scanned card with a changed field highlighted" />

# DescriptorPin

*Pins the tool descriptors an MCP client trusts, then reports silent mutation,
cross-server shadowing, instruction-shaped description text, and stdio
transport risk.*

[Install](#install) &nbsp;&middot;&nbsp;
[Commands](#commands) &nbsp;&middot;&nbsp;
[Finding classes](#finding-classes) &nbsp;&middot;&nbsp;
[The pin file](#the-pin-file) &nbsp;&middot;&nbsp;
[Limitations](#what-descriptorpin-does-not-do)

</div>

---

## The descriptor trust problem

A Model Context Protocol client reads a server's tool list and shows it to a
person who approves it once. Every call after that approval resolves tools by
name. Nothing in the protocol asks the client to notice when a description
changes, when a second server starts exposing a tool with a name that is
already trusted, or when a description stops documenting a tool and starts
instructing the model that reads it.

DescriptorPin treats the approved state as the anchor. It records a canonical
hash for every tool descriptor at approval time, and on each later scan it
reports the shapes that differ from that anchor. The output names fields and
servers; it never returns a single opaque score.

## What it checks

| Property | Mechanism |
|---|---|
| A tool that was approved, then silently changed | Canonical hash per descriptor compared by `src/descriptorpin/mutation.py` against the pin written by `src/descriptorpin/pin.py` |
| Two servers claiming the same bare tool name | Grouping across servers in `src/descriptorpin/shadow.py`, with the precedence risk stated |
| Description text shaped like instructions to the model | Named structural signals with weights in `src/descriptorpin/poison.py` |
| A server declared over stdio | Transport review in `src/descriptorpin/transport.py`, because a config entry can become command execution |
| Hash churn from key order or whitespace | Deterministic serialisation in `src/descriptorpin/canon.py` so only value changes move the hash |
| Stable, diffable reports | Line-oriented rendering in `src/descriptorpin/report.py`, no clock and no randomness |

## Install

```
git clone https://github.com/propavingk/DescriptorPin
cd DescriptorPin
python -m unittest discover -s tests -v
```

