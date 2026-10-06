# Features and limits

The native server is reused across VS Code and Zed. A native capability is
available for Zed acceptance only when the editor exposes and applies it.
This table distinguishes observed editor behavior from remaining validation.

| Feature | Current Zed evidence |
| --- | --- |
| Acore file recognition and syntax | Z1 passed in Zed 1.21.0 on macOS ARM64 with the rebuilt grammar: four profiles display syntax colors. TOML/JSON/YAML/Pkl retain their identities. Ten golden parser cases and all 14 playground files pass. |
| Brackets, indentation, outline and structural selection | Z1 manual checks passed: class and nested page/action brace pairing, two-space indentation, four-profile outlines, comment toggling and selection growth to an action body. Query checks also cover text objects and all three bracket pairs. |
| CSS injection | Styles and quoted braces parse; the CSS injection capture is checked. CSS rendering is not separately certified. |
| Incomplete editing states | Unfinished string/body highlighting remains usable and the outline recovers after repair. Incremental Unicode/CRLF deletion-and-repair trees match fresh parses. |
| Thirteen starter snippets | L6 adds SQLite/evolution/advanced PostgreSQL, security, managed, callbacks, stores/migration, named routes and the application companion. Default expansions compile in selected profiles; grammar queries cover all thirteen. Original four-profile expansion/tab-stop acceptance is retained. Same-session Zed extension rebuilds can duplicate suggestions; see INSTALL.md. |
| Native stdio server and settings | Z2 passed in installed Zed: configuration/backend/frontend/database buffers open with `languageId: acore`, UTF-16 and diagnostics. Explicit and worktree-relative overrides, PATH fallback, precedence over a wrong PATH candidate, literal arguments/environment, initialization selections and live workspace configuration forwarding pass. |
| Native compatibility and startup errors | Z2 checks `--version-json` before LSP initialization, including explicit overrides. Missing/non-executable/wrong-format paths, wrong server/protocol, malformed initialization options and absent PATH discovery produce host errors; rejected candidates receive no initialize. Compatibility checking is separate from artifact digest verification. |
| Trust and execution | Z2 confirms Restricted Mode blocks the project server and metadata probe. Allowed worktrees initialize the native server with `workspaceTrusted: false`; unsafe overrides are rejected. Explicit CLI execution remains separate. |
| Lifecycle and recovery | Z3 passed the editor restart action in Zed 1.22.0: existing buffers reattach with unsaved edits across all four profiles. The tested initialization-selection change also replaces the process and resynchronizes buffers. Keep project reopening as recovery for the older 1.21.0 gap or other disconnected startup changes. Owned audit processes exit after disabling the server. |
| Hover and diagnostics | Z3 displays compiler hover, unsaved invalid diagnostics and recovery in configuration/backend/frontend/database files. Database checks remain offline. |
| Semantic tokens | Z3 receives current tokens and visibly renders all four profiles with `full` semantic mode, independently of Tree-sitter colors. `combined` is recommended so grammar colors cover punctuation/comments and unfinished states. Native checks validate UTF-16 token bounds. |
| Configuration inlay hints | Z4 passed fresh/warm hints, unsaved value and imported-type edits, undo, explicit annotation suppression, settings off/on, close/reopen and restart/rebuild. Unique native hint lists and current refreshes are captured. The earlier heavily reloaded Z3 window duplicated hints; Z4 did not reproduce it in a fresh window, and does not claim every host cache/reload case is fixed. Configuration only. |
| Typed completion and signatures | Z3 passed Boolean filtering, backend contract-type completion, frontend action-event filtering and database enum-argument filtering. Signatures display configuration calls, backend directives, authored frontend components and database declarations with the active parameter. L1–L6 add primitive/component-event signatures, named active parameters, String/List method help, typed form/store/route commands and engine-specific database constructors. |
| Definition and type definition | Z3 opens physical configuration classes, backend models, imported frontend components and imported database schemas. Type navigation reaches authored configuration/backend classes and database enums; nested owners stay separate. Z4 suppresses unsupported virtual builtin/library/SDK destinations; physical destinations are retained. |
| References and occurrence highlights | Z3 displays physical-source reference results and highlights. Configuration classes and imported frontend/database declarations cross files. An implicit generated backend entity is a separate symbol from its model: model reference search does not list every generated entity use. |
| Document/workspace symbols | Zed's document outline uses the grammar queries (four-profile Z1 acceptance and Z3 configuration outline); no `textDocument/documentSymbol` UI request was observed. Native document-symbol protocol checks pass. Z3 workspace search uses LSP and finds unsaved renamed symbols in all four profiles. |
| Formatting | Z3 applies native indentation edits and preserves comments, Unicode and CRLF; a second pass leaves saved bytes unchanged. Native regressions cover lossless/idempotent formatting in all four profiles. Formatting is conservative and does not promise canonical operator spacing or expression rewriting. |
| Symbol rename | Z3 applies configuration class/binding renames, backend model/generated-entity updates, frontend action/imported-component renames and database column/imported-schema renames. UTF-16 positions after emoji and CRLF save preservation pass. A scope collision is rejected without edits. Authored, compiler-validated cases only; implicit/projected/generated declarations are not generally renameable. |
| Quick fixes and freshness | Z3 applies configuration reference, backend enum and unambiguous frontend binding repairs and clears diagnostics on unsaved buffers. Database automatic repairs are not implemented. Native regressions reject stale/forged diagnostics and unsafe rename candidates; real Zed receives snapshot-change/cancellation responses during editing and resumes on current snapshots. |
| Configuration file rename | Z4 real Zed sends will/did-rename, applies versioned semantic import edits and preserves comments/strings for valid same-directory configuration candidates. Native rejection protects edits, but Zed still moves the file on disk when the refactor fails. Repair errors first, review/save consumers, and rename back to recover a rejected move. Other-profile file refactors and directory moves are unsupported. |
| Type hierarchy | Z4 confirms no advertised capability or matching action in Zed 1.22.0. Unavailable in this adapter; native hierarchy/stale-item checks pass separately. |
| Manifest authoring and coexistence | L3 registers the server for existing TOML without reclassifying it. Mac Zed displays manifest hover/field completion, accepted edits and fresh Audience choices from unsaved TOML. Ordinary TOML receives no Axiom vocabulary/hover/formatting/diagnostics; JSON/YAML/Pkl retain their usual providers. |
| Virtual library/contract/SDK navigation | Z4 disables virtual destinations to prevent Zed opening empty editable filesystem buffers. Physical destinations and SDK signature/state/digest hover remain supported. No Zed content provider or projection/contract view exists; native digest/provenance/staleness/read-only guards and existing VS Code providers pass shared regressions. Requires the Z4-compatible native server. |
| Contract/graph panels | No Zed presentation implemented. |
| Explicit CLI checks and discovery | Z5 passes actual Zed tasks for configuration/backend/frontend/database, nested owners, literal paths with spaces/shell punctuation, compatibility/help, invalid saved input, rejected outer roots and missing CLI. Tasks use saved files without saving buffers, report JSON/exit status in the terminal, and have no automatic hooks. No CLI Problems-panel importer is implemented. |
| SDK IDE preparation | Z5 passes explicit interface emission/preparation, prepared signature/digest hover, stale-source detection and explicit recovery. Physical helpers/receipt are written only by the CLI action; no guest execution, authority grant or replacement of owning native configurations occurs. Virtual SDK views remain unavailable. |
| Native extraction refresh | Z5 passes explicit Go/FastAPI refresh tasks and physical navigation/type reuse with a matching CLI/server compiler fingerprint. Old compiler caches and changed saved inputs are stale; missing tools fail without replacing the old cache. Passive editing does not execute extractors. Acceptance uses local fixture extractors, not production native toolchain certification. |
| Physical native language providers | Z5 observes existing TypeScript `vtsls` contract completion, U16 hover and generated physical definition navigation. Rust/Python/Go retain their normal languages and send no Acore didOpen. Full typing/toolchain acceptance for those providers is not claimed; the Rust fixture lacks a Cargo workspace. Providers keep their own normal discovery/download/indexing behavior. |
| Verified server download/cache and updates | Z6 implements immutable release/platform/size/SHA-256 pins, streaming raw assets, atomic promotion and verification on every reuse. Actual Mac Zed rejects corrupt/truncated/missing assets, repairs a cache and restarts offline with executable permissions restored. Version/hash caches are retained for explicit rollback. The 0.1.1 Mac native ZIP is public for manual installation; automatic raw downloads, registry installation and other OS acceptance remain pending. |

Passive editing uses compiler snapshots without executing foreign code,
launching a runtime, resolving remote dependencies or contacting a database.
Domain limitations still apply: database authoring is offline; some projected/generated declaration refactors remain unavailable.
Native rename validates an authored candidate and rejects stale or unsupported
edits. CLI checks use saved files; LSP queries can use unsaved buffers.
See [typed-editing walkthrough](TYPED_EDITING.md) for repeatable editor checks.

See [E7/configuration compatibility](E7_CONFIGURATION.md) for repeatable checks.

See [explicit CLI tasks](CLI.md) and [foreign workflows](FOREIGN_WORKFLOWS.md).

Z0–Z5 are complete for the private macOS ARM64 alpha, using Zed 1.22.0 for Z3–Z5.
Z6 installer/release preparation is implemented; the adapter license is Apache-2.0 and automatic native activation remains disabled; use the separately published 0.1.1 ZIP. See [distribution and recovery](DISTRIBUTION.md).
Z7 macOS ARM64 release acceptance and performance measurements are recorded in
[TESTING.md](TESTING.md) and [PERFORMANCE.md](PERFORMANCE.md). Diagnostic latency
exceeds the proposed smaller-corpus budget; other measured targets pass. Physical Intel macOS, Linux x64 and
Windows x64 acceptance remain pending; no other architecture is certified.

## L1–L6 authoring

Adapter 0.1.3 and its public grammar use the published native 0.1.1 release.
The historical 0.1.0 ZIP predates these changes. Shared tests cover
descriptive/authored hover, prefix/list/bracket Audience edits, full-path manifest
help and captured choices, SQLite/advanced database signatures, selected evolution
diagnostics/navigation/formatting, managed bindings, frontend callbacks and
form/store/route/migration references with compiler-validated rename. Registry
properties/styles/methods follow selected targets. See [AUTHORING.md](AUTHORING.md).

Evolution history selection binds captured bytes; it does not replace CLI history
chain checks. Compiled baselines have no fabricated physical symbol definitions.
Structural record/form keys and generated declarations are not generally
renameable. L7–L9 implement private artifacts, graph/impact and explicit CLI workflows as
described below. The L10 Mac release is delivered; other platforms remain deferred.

## L7–L9 private inputs and workflows

Adapter 0.1.3 attaches the matching native server to recognized private JSON
without reclassifying the language or supplying Acore responses to ordinary JSON.
Forty roles have shared wire schemas, field/enum/reference completion, hover,
diagnostics, physical definitions and bounded inspection. Generated/signed inputs
remain inspection-only in Acore; no signature or execution authority is inferred.

Advanced/SQLite objects, managed/delivery/integration and frontend form/store/
persistence/policy/route/guard/session/navigation relationships are available in
the shared graph report. D10 persistence and compatible frontend links require
current exact schemas and public artifact identities; stale mappings are excluded.
Zed uses `editor report`; an equivalent custom graph panel is not implemented.

The new explicit workflow recipe saves all buffers, validates typed inputs using
the actual CLI, checks matching compiler identity and fences saved inputs before
execution. Real application suites require nonzero assertions; compiler smoke is
separate. Eight runner checks and 21 adapter tests pass on Apple Silicon macOS.
Visible JSON hover and enum insertion, the saved inspection task and a real
two-assertion application task also passed in the Zed review window. Other OS, hosted Actions and registry acceptance remain pending. See
[WORKFLOWS.md](WORKFLOWS.md) for setup, invocation, cancellation and limits.
