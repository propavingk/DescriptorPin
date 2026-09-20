# Recipes: running the gate in CI

## GitHub Actions

```yaml
name: descriptor-check
on:
  pull_request:
    paths:
      - "client-config.json"
      - "client-config.pin.json"
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: PYTHONPATH=src python -m descriptorpin scan client-config.json -p client-config.pin.json
```

The job fails on any finding by design. Exit code 2 means the job definition
or the input shape is wrong, and should be treated separately from a finding.

## Pre-commit hook

```
#!/bin/sh
PYTHONPATH=src python -m descriptorpin diff client-config.json -p client-config.pin.json || exit 1
```

Use `diff` in the hook so day to day commits only block on mutations; run
the full `scan` in CI where additions and shadowing are also visible.
