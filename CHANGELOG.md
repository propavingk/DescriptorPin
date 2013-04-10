# Changelog

All notable changes to DescriptorPin are documented here. The format follows
Keep a Changelog, and the project uses semantic versioning.

## [Unreleased]

### Changed

- Descriptor drift wording is under review for the next patch.

## [1.0.1] - 2026-06-30

### Fixed

- The canonicalizer now folds duplicate keys deterministically instead of
  depending on the dict iteration order.

## [1.0.0] - 2025-10-14

### Added

- Stable CLI contract for canon, scan, pin, and version, exit codes 0/1/2.
- scripts/verify.py as the repository quality gate.

## [0.9.5] - 2024-03-27

### Changed

- Maintenance release: documentation pass and test hygiene.

## [0.9.0] - 2022-07-19

### Added

- Multi-inventory diff mode comparing two descriptor snapshots.
- JSON output for the drift report.

## [0.8.0] - 2020-12-01

### Added

- Drift view in the report, sorted by field path.
- Shadow detection for pinned fields that no longer exist upstream.

## [0.7.0] - 2019-04-16

### Added

- Sample inventories and the verify gate.
- Poison checks for values that break canonical folding.

## [0.6.0] - 2018-10-03

### Added

- Test suite covering canon, inventory, and the CLI.
- Makefile targets for test and verify.

## [0.5.0] - 2017-08-22

### Added

- Report renderer with stable field paths.
- CLI entry point with subcommands.

## [0.4.0] - 2016-11-07

### Added

- Shadow field detection in mutated inventories.

## [0.3.0] - 2015-06-18
