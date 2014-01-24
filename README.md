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

