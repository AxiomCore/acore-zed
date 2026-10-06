# Changelog

## 0.1.1

Reject unknown language-server IDs before reading worktree settings or launching
the native server. Update installation and maintenance instructions for the
public Mac ARM64 Acore LSP 0.1.0 ZIP. The adapter and native server have separate
versions; explicit binary path/PATH selection remains the initial install route.
Automatic native downloads and other OS acceptance remain pending.

## 0.1.0

Initial macOS ARM64 development release of the Apache-2.0 Acore Zed adapter.
Provides Tree-sitter syntax/structure, snippets, native stdio connection and
compiler-backed editing for configuration, backend, frontend and database
projects. Adds configuration hints/file refactors within the documented host
limits, explicit CLI task templates, and a verified pinned native installer
whose public downloads remain disabled pending separate redistribution review.

Includes public offline examples, a real native smoke check, installation,
testing, update, rollback and shared-architecture guides. macOS ARM64 desktop
acceptance is recorded on Zed 1.22.0. Other operating systems, Intel macOS and
registry installation remain pending. Diagnostic refresh exceeds the proposed
smaller-corpus latency budget; see [performance](docs/PERFORMANCE.md).
