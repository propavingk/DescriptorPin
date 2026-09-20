# Cookbook: auditing a client config inventory

An MCP client config lists the servers and tools a client trusts. This is a
repeatable way to pin and re-scan one.

## 1. Pin the approved state

```
python -m descriptorpin pin client-config.json -o client-config.pin.json
```

Review the pin like any trust change and commit it. The approval records in
the file name who signed off.

## 2. Scan on every change to the config

```
python -m descriptorpin scan client-config.json -p client-config.pin.json
```

Exit code 1 means at least one finding. Read MUTATION first: a pinned tool
whose hash moved after approval is the rug pull shape.

## 3. Review shadowing before adding a server

```
python -m descriptorpin shadow client-config.json
```

A bare name claimed by two servers is the finding. Decide the resolution
order or rename a tool before the config lands.

## 4. Keep the report in the change request

Attach the scan output. The lines are stable, so reviewers can diff two
scans of the same config mechanically.
