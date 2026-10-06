# Native connection troubleshooting

Use **zed: open log** for the startup error. Confirm the configured executable
independently:

```sh
/absolute/path/to/acore-lsp --version-json
file /absolute/path/to/acore-lsp
shasum -a 256 /absolute/path/to/acore-lsp
```

The expected metadata has `serverVersion: "acore/…"`,
`protocolVersion: "axiom-editor/v1"` and a 64-character hexadecimal
`compilerVersion`. Compare the file's digest with the maintainer's receipt.
The extension's version and native compiler fingerprint are separate.

| Observed error | Recovery |
| --- | --- |
| Needs a standalone executable | Set `lsp.acore-lsp.binary.path` or put a compatible `acore-lsp` on the worktree PATH. The private alpha has no approved download release enabled. |
| No such file or directory | Correct the path. An explicit override takes priority over PATH and does not silently fall back. |
| Permission denied | Check executable permissions on the verified native artifact. |
| Exec format error / wrong host architecture | Use an artifact for the execution host. Only macOS ARM64 acceptance has been performed. |
| `--version-json failed` | Check the native executable or wrapper independently. A malformed executable produced status 127 on the tested Mac; other hosts may report an OS format/architecture error. |
| Does not identify itself as acore-lsp / invalid version metadata | Use the standalone language server. A wrapper must answer `--version-json` without its usual stdio arguments. |
| Incompatible editor protocol | Select a server supporting `axiom-editor/v1`; changing the extension version alone does not update the server. |
| Native server lacks virtual-document navigation opt-out | Update to the Z4-compatible native server and adapter together. A protocol-compatible older E7 server cannot safely suppress virtual targets for Zed. |
| Virtual documents cannot be opened safely | Remove `virtualDocumentNavigation` from startup/live settings or set it to `false`. Use hover and physical navigation. |
| Missing compiler fingerprint | Use a native build with the complete version interface. |
| Initialization options must be an object | Use a JSON object, with native selection/settings fields of the documented types. |
| Read-only server mode | Remove `workspaceTrusted` from initialization/live settings or set it to `false`. Use explicit CLI tasks for execution. |
| Waiting for worktree to be trusted | Review the project's settings in Zed's security modal. Restricted Mode deliberately blocks the project server and metadata query. |

After fixing startup settings, use **editor: restart language server** from an
active Acore file. Z3 verified that action in Zed 1.22.0 with unsaved buffers
across all four profiles. If it remains disconnected, reopen the project in a
new Zed window. Zed 1.21.0 failed automatic reattachment in an earlier Z2
settings-change case; a new process alone does not establish buffer recovery.

If a database project unexpectedly offers generic keywords, verify its selected
entry, especially when multiple files contain a `database` declaration. Rebuild
the Z3 adapter: it retains initialization selections when Zed sends an empty
live-settings update. Explicit `lsp.acore-lsp.settings` overrides still win.

The command palette ranks recent actions. Select the exact **go to definition**
action; **go to type definition** is a different request and may appear first.
For signature help, place the caret inside the argument list. A null result
outside a call or for an unsupported builtin overload is expected. Native
snapshot-change errors request a retry after current diagnostics arrive.
Quick fixes are offered only where the compiler can validate a repair; a
diagnostic does not imply an available fix.

An executable that never finishes `--version-json` can leave startup pending:
the reviewed Zed process API has no timeout parameter. Correct the binary and
restart the server/editor after saving work. No arbitrary runtime command is
invoked by the compatibility query.

Dev extension reloads can duplicate snippet suggestions. Z3 also saw duplicated
hints in a heavily reloaded window. Z4 passed hint edits/imports, annotations,
off/on, close/reopen and restarts in a fresh worktree without duplicates; it
does not fix every host cache issue. Reopen an affected project in a fresh
window. A failed startup can leave host-cached hints visible, so confirm that
current hover/diagnostics work after recovery. See [installation notes](INSTALL.md).

Zed can move a configuration file even when its import refactor is rejected.
Rename it back, repair diagnostics and retry, or update/recheck imports
explicitly. Typed manifest attachment, hierarchy and virtual content views
are unavailable in this adapter. See [E7/configuration limits](E7_CONFIGURATION.md).
Z0–Z5 passed on macOS ARM64 in Zed 1.22.0. See [installer recovery](DISTRIBUTION.md)
for Z6 download/cache failures. Final performance, public promotion and other
host acceptance remain later gates.
