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

