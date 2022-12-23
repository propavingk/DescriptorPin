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

Standard library only. There is nothing to install at runtime and no network
access anywhere in the code.

## Commands

```
python -m descriptorpin pin    samples/inventory_clean.json -o samples/pin.json
python -m descriptorpin scan   samples/inventory_mutated.json -p samples/pin.json
python -m descriptorpin diff   samples/inventory_mutated.json -p samples/pin.json
python -m descriptorpin shadow samples/inventory_mutated.json
python -m descriptorpin version
```

| Command | Reads | Reports |
|---|---|---|
| `pin` | one inventory | writes a pin file recording the approved descriptor state |
| `scan` | a pin and an inventory | every finding class below |
| `diff` | a pin and an inventory | rug pull mutations only |
| `shadow` | one inventory | cross-server name collisions only |
| `version` | nothing | the version string |

Exit codes: `0` clean, `1` findings present, `2` usage or input error.

## A real scan

The bundled samples ship a clean inventory, a pin recorded from it, and a
mutated inventory that differs in the ways the tool exists to catch. Running
`make run` on this repository prints:

```
MUTATION files-local/read_file: pinned bcf8a5056056 scanned 4a3b9edca34f
  field description changed
    pinned:  Read the contents of a file at the given path and return it as text. Accepts an absol...
    scanned: Read the contents of a file at the given path and return it as text. Before doing any...
ADDED helper-plugin/query: scanned 58db016359a0, not in pin
SHADOW query: claimed by 2 servers (helper-plugin, search-index)
  precedence risk: client resolution order decides the winner
POISON files-local/read_file: score 8, 3 signals
  signal concealment (weight 3): instructs to hide, conceal, or not disclose
  signal priority_override (weight 3): asserts precedence over previous or other instructions
  signal imperative_opener (weight 2): sentence opens with imperative 'do not'
TRANSPORT helper-plugin: transport 'stdio' flagged, launched as a local subprocess from client config, so config can become command execution
summary: 4 findings (1 mutation, 1 shadow, 1 poison, 1 transport)
```

One mutation, one shadow, one poison, one transport, each line naming the
tool or server it concerns. The scan exits `1`.

## Finding classes

| Class | Shape it describes | First action |
|---|---|---|
| MUTATION | A pinned tool whose canonical descriptor hash changed | Read the field diff, then re-approve or reject |
| ADDED | A tool present in the inventory but absent from the pin | Approve it explicitly or remove the server |
| SHADOW | One bare name claimed by two or more servers | Decide the resolution order or rename a tool |
| POISON | Description text that fires one or more named instruction signals | Read the fired signals and judge the text |
| TRANSPORT | A server declared over stdio | Treat the config entry as executable content |

## The pin file

`pin` records, per tool: the server-qualified key, the canonical descriptor
hash, a truncated digest for reading, the canonical descriptor itself, and an
approval record with the approver and their note. Keeping the canonical
descriptor in the pin is what lets a later diff show the exact field that
changed, instead of only reporting that something did.

The pin is a plain JSON document. Commit it, review it in pull requests, and
treat a change to it as a change to what the client trusts.

## Canonicalisation

Two servers can serialise the same descriptor with different key order or
insignificant whitespace. `canon.py` folds those differences before hashing,
so the pin does not churn on formatting and a real value change cannot hide
behind reordering. The fold is deterministic: identical input produces
byte-identical output, and the reports that follow sort deterministically too.

## Quality gate

`scripts/verify.py` is the repository's mechanical gate. It checks the SVG
assets, the em dash sweep, the README rules, and the label overlap rule in
the assets. Run on this repository it prints:

```
check 1 svg-parses: OK (2 svg)
check 2 no-filters: OK
check 3 comment-hyphen: OK
check 4 em-dash: OK
check 5 pandoc-attr: OK
check 6 marketing: OK
check 7 svg-a11y: OK
check 8 label-overlap: OK
verify: 8 checks, 0 failures
```

`make test` runs the unit suite, `make verify` runs the gate, `make run`
reproduces the scan above against the samples.

## Repository layout

```
descriptorpin/
  src/descriptorpin/
    canon.py          canonical descriptor serialisation
    inventory.py      strict inventory parsing with usage-grade errors
    pin.py            pin file writer and verifier with approval records
    mutation.py       rug pull detection and field level diff
    shadow.py         cross server name collision detection
    poison.py         named structural instruction signals
    transport.py      transport review, stdio flagged
    report.py         deterministic line oriented rendering
    cli.py            subcommands, exit codes
  samples/            clean inventory, mutated inventory, recorded pin
  tests/              suite per module and for the CLI
  scripts/verify.py   the eight check quality gate
  docs/assets/        logo and drift diagram
  Makefile            help, test, verify, run, clean
```

## Why not hash the raw descriptor bytes

Raw bytes move when key order moves, and a pin that churns on formatting is a
pin nobody reads. Folding through a canonical form first keeps the hash
sensitive to values and insensitive to serialisation.

## Why not one poison score

A single number invites a threshold, and a threshold invites false comfort.
`poison.py` reports which named signals fired, each with its own weight, and
leaves the judgement to the reader. A heuristic can fire on innocent text and
can miss a careful attacker; saying so is part of the output.

## What DescriptorPin does not do

- It does not contact the MCP server. It reads inventory files on disk, which
  is why it runs in CI and on a laptop with no network.
- It does not verify cryptographic signatures. Descriptor integrity here is
  against the pin you approved, not against a signed publisher chain.
- It does not classify intent. The signal and shape wording is deliberate:
  the tool reports structure, and the reader judges.
- It does not resolve shadowing by picking a winner. The collision is the
  finding; the client's resolution order decides, and that order is often
  undocumented.

## Contributing

One topic per commit, conventional prefixes, tests for behaviour changes, and
no network access in the code. Run `make test` and `make verify` before a
pull request. The suite is standard library `unittest` only.

## License

MIT. See `LICENSE`.

<!-- draft note 1053 -->
