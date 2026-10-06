# Acore for Zed

Compiler-backed authoring for Acore configuration, backend, frontend and database
projects. The Apache-2.0 Zed adapter launches a separately supplied compatible
native `acore-lsp`. Tree-sitter supplies syntax, indentation, outline and text
objects; the shared compiler supplies types and validated edits.

**Accepted host:** Apple Silicon macOS 26.2 with Zed 1.22.0. Linux, Windows,
remote execution and physical Intel macOS acceptance remain pending. The native
server and optional CLI have separate distribution and licensing. Automatic
public native downloads are disabled until their release is approved. Registry
publication requires a human-submitted PR and maintainer merge; this source
candidate is usable as a dev extension now.

## Install and try it

Follow [INSTALL.md](docs/INSTALL.md) for the exact Git/dev install steps and
verified server selection. In Zed run **zed: install dev extension**, then open
[the four small examples](examples/README.md) with the supplied server configured
in project or user settings. Use **zed: open log** for startup errors.

```json
{
  "lsp": {
    "acore-lsp": {
      "binary": { "path": "/absolute/path/to/acore-lsp" }
    }
  },
  "languages": {
    "Acore": {
      "formatter": "language_server",
      "semantic_tokens": "combined",
      "inlay_hints": { "enabled": true }
    }
  }
}
```

The compatible server must report `axiom-editor/v1` and
`editorFeatures.virtualDocumentNavigationOptOut: true`. Earlier E7 binaries
without that safeguard are rejected. The adapter selects an explicit path,
then the worktree PATH, then any enabled reviewed release. Verify an override
against the maintainer's SHA-256 receipt.

## Features and limits

Accepted editing includes four-profile diagnostics, typed completion,
supported signatures, hover, physical definition/type navigation, references,
workspace symbols, semantic colors, conservative formatting, validated authored
symbol rename and supported quick fixes. Configuration adds inlay hints and
valid same-directory file refactors. Syntax/brackets/indentation/outline/text
objects and four snippets are available. Copyable project-local CLI tasks are
optional and run explicitly against saved inputs.

Only `.acore` is registered. Saved manifests inform project ownership; their
unsaved buffers retain ordinary language tooling. Zed has no implemented type
hierarchy, typed manifest attachment, read-only virtual SDK/library/contract
provider or graph panel in this adapter. Virtual navigation is disabled;
physical navigation and SDK hover remain available. A rejected configuration
file refactor does not stop Zed moving the file. Read the full
[feature matrix](docs/FEATURES.md) before relying on a workflow.

Passive editing uses compiler snapshots. It does not run foreign code,
extractors, a runtime, remote dependency resolution or database connections.
Zed governs worktree trust; the adapter always supplies `workspaceTrusted: false`.
Effectful work uses explicit CLI commands. Large-project diagnostic refresh can
still take seconds; see [performance/support](docs/PERFORMANCE.md).

## Developer and maintainer guides

- [Install from Git / dev extension](docs/INSTALL.md)
- [Settings and server compatibility](docs/SETTINGS.md)
- [Test source, real native LSP and Zed](docs/TESTING.md)
- [Typed editing walkthrough](docs/TYPED_EDITING.md)
- [Configuration hints, manifests and file refactors](docs/E7_CONFIGURATION.md)
- [Explicit CLI tasks](docs/CLI.md) and [foreign workflows](docs/FOREIGN_WORKFLOWS.md)
- [Verified distribution, offline recovery and rollback](docs/DISTRIBUTION.md)
- [Publish to the registry](docs/PUBLISHING.md) and [ship future updates](docs/MAINTENANCE.md)
- [Shared VS Code/Zed architecture](docs/ARCHITECTURE.md)

The extension source contains no native executable or private compiler/runtime
source. Public source releases are exported from an explicit allowlist with
fresh history. The grammar has separate Apache notices; downloaded native tools
are not covered by this adapter's license. See [LICENSE](LICENSE), [NOTICE](NOTICE)
and [third-party notices](THIRD_PARTY_NOTICES.md).
