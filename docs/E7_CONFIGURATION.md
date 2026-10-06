# E7 editing and configuration compatibility

Z4 is complete for the private macOS ARM64 alpha in Zed 1.22.0. Configuration
inlay hints and valid same-directory configuration file refactors are tested
in the editor. L3 adds typed TOML manifest attachment and unsaved overlays. Type hierarchy
and virtual document views retain the host limits below. Other operating systems remain pending.

## Enable and test configuration hints

Select the Z4-compatible native server and enable hints in the owning
worktree's `.zed/settings.json`:

```json
{
  "lsp": {
    "acore-lsp": { "binary": { "path": "/absolute/path/to/acore-lsp" } }
  },
  "languages": {
    "Acore": {
      "semantic_tokens": "combined",
      "inlay_hints": { "enabled": true }
    }
  }
}
```

In a configuration `.acore` file, try:

```acore
emoji = "é😀"
count = 2
explicit: Int = 3
flag = true
class Parent { value: Int = 1 }
class Child extends Parent { extra: String = "ok" }
child = Child {}
```

After analysis, `count` shows `: Int`, `flag` shows `: Boolean`, and `child`
shows `: Child`. Explicitly annotated bindings do not receive a second type.
Literal strings can display their literal type. Change `count` to `true`
without saving: its hint changes to Boolean. Add `: Boolean` to its name:
the inferred hint disappears. Undo restores the inferred result.

Hints also follow unsaved imported configuration types. Z4 checked a warm
open, edits/undo, explicit annotations, settings off/on, buffer close/reopen,
two server restarts and a rebuilt adapter in a fresh acceptance worktree.
Native hint lists contain no duplicate positions/labels. Analysis is
asynchronous; a previous hint may remain briefly until current results arrive.

Z3 had observed duplicated hints in a heavily reloaded development window.
Z4 did not reproduce them in its fresh window. This is not a claim that every
Zed reload/cache bug is fixed. If a development session accumulates hints,
reopen the project in a new window; save work before restarting the editor.
Configuration hints do not imply backend, frontend or database hint support.

## Rename a configuration source file

Use the project panel's **Rename** action on one `.acore` source at a time.
For a clean generic configuration project, Zed sends `workspace/willRenameFiles`,
applies the server's versioned import edits, moves the file, and sends
`workspace/didRenameFiles`. For example:

```acore
Model = import("model.acore")
result = Model.value
text = "model.acore" // import "model.acore"
```

Renaming `model.acore` to `renamed.acore` changes the actual import. The ordinary
string and comment remain unchanged. Review and save the edited consumers;
Zed can leave them dirty even though the file has already moved on disk.

The server supports a new `.acore` filename in the same directory, captured
generic configuration consumers, current snapshots and a valid candidate.
Existing destinations, directory/project moves, conflicting edits and invalid
configuration are rejected. This does not extend file refactoring to the
backend/frontend/database profiles or arbitrary files.

**Zed 1.22 does not cancel the filesystem rename when the server rejects its
import refactor.** Z4 demonstrated this with an unsaved configuration error:
the file moved, the import stayed unchanged, and missing-import diagnostics
appeared. Repair diagnostics before renaming and review the resulting imports.
If a rejected rename has already moved a file, rename it back, repair the
configuration, and retry; alternatively update and validate the imports
explicitly. The native rejection protects proposed edits, not Zed's disk move.

## Type hierarchy

The tested Zed client has no type-hierarchy capability or matching palette
action. The adapter does not provide a hierarchy view. Native hierarchy and
stale-item rejection remain available to supporting clients. Use physical
**go to type definition**, references and the structural outline in Zed.

## Virtual source navigation

The VS Code client renders `acore:`, `axiom-contract:` and `axiom-interface:`
documents through content providers. This Zed adapter has no equivalent.
The tested host rejected `acore:base` and interpreted an SDK projection URI as
a filesystem path, opening an empty editable buffer.

The Z4 adapter therefore initializes the native server with
`virtualDocumentNavigation: false`. Definition, type-definition and reference
results retain physical `file:` destinations and omit virtual destinations.
Zed may show authored references when definition has no physical target.
Prepared SDK hover still shows its signature, state and interface digest;
valid physical origins remain navigable. No projected temporary files are
written and no read-only projection is presented as an editable source.

Do not enable that flag in Zed settings. The adapter rejects values other than
`false`, including live overrides. It also requires
`editorFeatures.virtualDocumentNavigationOptOut: true` from `--version-json`;
an older E7 binary is rejected before LSP initialization. Update the adapter
and native server together. The flag is fixed for a server session. Native
clients that omit it retain the existing virtual navigation behavior.

Projection generation, digest/provenance, stale-input fences and read-only
rename guards remain native services. Z4's native and VS Code regressions
verify them separately. Zed virtual content views, contract inspectors and
graphs are not implemented.

## Manifests and other language providers

Adapter 0.1.2 registers the same native server for Acore and existing TOML.
This supersedes Z4's Acore-only manifest attachment limit. `AxiomDeps.toml` stays
TOML and receives Axiom completion, hover, diagnostics and unsaved overlays.
Ordinary TOML receives no Axiom vocabulary/hover/formatting/diagnostics. Other
host providers can remain enabled; JSON/YAML/Pkl retain their ordinary providers
and do not gain buffer attachment from this change.

Saved recognized manifests/locks continue to inform the owning Acore snapshot.
An unsaved valid backend manifest now updates its open Acore owner: declared
Audience choices change without saving. Invalid TOML or invalid manifest fields
produce diagnostics, and repairing the buffer restores the current snapshot.
See [AUTHORING.md](AUTHORING.md) for repeatable L1–L6 checks and explicit evolution
settings. `configurationFiles` still refines recognized native formats; it does
not define a replacement TOML language or automatically attach JSON/YAML.

Native TOML manifest completion/navigation, filename associations, YAML
migration-only behavior, static `PklProject` queries and stale contract/lock
checks pass protocol regressions. They are not Zed UI claims. Explicit saved
CLI checks are described in [CLI.md](CLI.md); real-Zed task acceptance is Z5.

See [settings](SETTINGS.md), [features](FEATURES.md) and
[troubleshooting](TROUBLESHOOTING.md). Host API references:
[extension API 0.7.0](https://docs.rs/zed_extension_api/0.7.0/zed_extension_api/trait.Extension.html),
[language settings](https://zed.dev/docs/configuring-languages),
[tested Zed LSP store](https://github.com/zed-industries/zed/blob/76659a55a8c10ed355a070f8764a0b1733e3c115/crates/project/src/lsp_store.rs),
[extension adapter registration](https://github.com/zed-industries/zed/blob/76659a55a8c10ed355a070f8764a0b1733e3c115/crates/language_extension/src/extension_lsp_adapter.rs).
