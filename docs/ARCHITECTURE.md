# Shared compiler services and separate editor adapters

VS Code and Zed use the same compiler-owned editor service and standalone
`acore-lsp` protocol, `axiom-editor/v1`. Project ownership, immutable snapshots,
type projections, diagnostics, typed completion, hover, navigation, references,
validated edits and freshness checks belong to that shared native layer.
Neither client reimplements the domain type checker.

| Layer | VS Code | Zed |
| --- | --- | --- |
| Compiler/editor semantics | Shared native Acore services | Same services |
| Standard transport | Native stdio LSP | Native stdio LSP |
| Client adapter | TypeScript and VS Code language client | Rust compiled to WASI, Zed extension API |
| Syntax presentation | TextMate grammar and VS Code language configuration | Separate Tree-sitter grammar and queries |
| Packaging | VSIX / Marketplace | Zed extension repository / registry |
| Configuration hints | Native configuration hints through the host | Same native hints through Zed |
| Type hierarchy | VS Code provider | No tested Zed host surface |
| Typed manifest buffers | VS Code attachment | Native services exist; no generic-language attachment in this adapter |
| Virtual SDK/library/contract documents | VS Code read-only providers | Navigation disabled; physical navigation and SDK hover remain |
| Inspector/graph presentation | VS Code custom presentation | No Zed panel implemented |

The adapters are different code. Sharing semantics does not imply identical
features, binaries or packaging. Each release selects a separately recorded
native build; an installed VSIX may contain an earlier E7 candidate. Compare
`--version-json` and the SHA-256 receipts when exact build parity matters.
Zed requires `editorFeatures.virtualDocumentNavigationOptOut: true`, so older
E7 servers without that safeguard are rejected even if they use the same
protocol name. See [FEATURES.md](FEATURES.md) for actual host evidence.

Zed supplies `workspaceTrusted: false` and `virtualDocumentNavigation: false`.
Physical `.acore` editing remains available. Effectful operations use explicit
CLI commands, and the optional CLI has its own executable and distribution.
Extraction cache reuse requires a matching CLI/server compiler fingerprint;
the CLI path is not inferred from the server path.

## Where to make future changes

- Change domain semantics in the private native compiler/editor service; run
  shared regressions and acceptance in both editors, then release new native
  artifacts and update each adapter's reviewed pins/package.
- Change Zed launch/settings/install behavior in this Rust adapter. Test the
  WASI component and actual Zed; VS Code does not consume this client code.
- Change syntax in the grammar repository, regenerate/test its parser, publish
  its tested commit and update `grammars.acore.rev`. Queries/snippets live in
  the adapter and require a new adapter release.
- Change VS Code UI/providers in the VS Code extension separately. A Zed
  counterpart requires a host API that can support that presentation.

Public adapter and grammar source do not include native compiler/runtime source,
private evidence or their Git history. The adapter is Apache-2.0; the grammar
retains its Apache notices. A separately distributed native executable has its
own terms, dependencies and disclosure surface.
