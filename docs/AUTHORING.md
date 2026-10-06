# Acore authoring updates (L1–L6)

These updates use the shared native compiler in both VS Code and Zed. They
require native 0.1.1, alongside VS Code adapter 0.2.5 or Zed
adapter 0.1.3 and its matching public grammar, with Acore LSP 0.1.1.
The historical 0.1.0 ZIP predates these additions. Use the verified current native
release and a CLI with the matching compiler fingerprint for explicit workflows.

## Hover and signatures

Hover `String`, `Audience`, `SensitiveData`, a declaration, an argument, a
column or a supported frontend primitive/style property. The shared descriptors
show types, signatures, required/optional status, accepted values and profile or
registry provenance. Builtin help survives nearby incomplete source; authored
symbol details require a current resolved snapshot.

In VS Code use **Show or Focus Hover** from the command palette. In Zed use **editor:
hover**; with Vim enabled the displayed binding is `g h`. Pointer hover also
uses the same provider. For signatures, put the caret inside the argument list
and invoke the editor's signature-help action. Named frontend arguments select
their matching parameter even when written out of declaration order. Component
events include typed `on_<event>` callbacks. String/List methods, pure builtins,
managed backend steps and accepted form/store/route commands use typed help.
Builtin command methods are not authored declarations and cannot be renamed.

Existing backend `doc:` / `Field(..., doc: ...)` documentation and contiguous
`///` lines immediately before a resolved declaration appear in its hover.
A blank line or intervening ordinary comment ends that doc-comment association.
Documentation in strings or comments is not a reference. Unsupported hover
locations return no result; they do not evaluate dynamic expressions.

## Audience completion

For a backend manifest:

```toml
type = "backend"
audiences = ["mobile", "public-web"]
```

Try `audience: Aud`, `audience: Audience.`, or an element of
`SensitiveData(audiences: [ ... ])`. Select a complete reference. Names that are
not identifiers use bracket spelling, for example `Audience["public-web"]`.
Completion replaces the typed prefix and preserves surrounding quotes/brackets.
The nearest owning manifest supplies the vocabulary, including declared contract
audiences. An unsaved valid manifest updates an open Acore file in both hosts;
invalid manifests do not invent audience names. Audience arrays must stay sorted
and unique. Completion never grants an audience or runtime permission.

In Zed with Vim enabled, enter insert mode and run **editor: show completions**
(the host's displayed binding is `ctrl-x ctrl-o`). In VS Code use **Trigger
Suggest**. Wait for the current snapshot after changing a manifest.

## AxiomDeps.toml

The file stays TOML. Completion and hover cover the canonical schema's root,
application, contracts, packages, guest environments/registries/policy, extensions,
guest packages and requested permission families. Help is specific to the full
field path and project kind. Required fields sort ahead of optional ones;
constants such as `format = "axiom-deps/v2"` and compatible templates are inserted
where known. Open strings remain open; a placeholder is not a completed project.

Value choices include accepted types/targets/Booleans, compatible declared aliases,
bounded local paths and captured contract audiences/operations. A supplied
signature/public-key pair must verify before artifact-derived choices appear.
Missing or incompatible artifacts produce no fabricated choices. No remote
artifact is fetched by completion.

VS Code attaches to recognized filenames and explicit associations without
changing their language ID. Use an existing TOML language extension, such as
[Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml),
for TOML syntax and general tooling. A fresh VS Code profile without a TOML
provider labels the buffer Plain Text; Axiom's filename-based assistance still
attaches. The acceptance profile uses Even Better TOML 0.21.2 and verifies that
its ordinary-TOML diagnostics remain available alongside Axiom's manifest help.
VS Code disables that companion in Restricted Mode on the tested host. The
buffer then retains Plain Text identity while Axiom's passive manifest help
continues; executable overrides and execution tasks remain disabled.

Zed's server
registers for both Acore and the existing TOML language: recognized manifests
receive Axiom services and unsaved overlays; ordinary TOML receives no Axiom
vocabulary, hover, formatting or diagnostics. Existing host TOML providers can
remain selected. JSON/YAML/Pkl retain their normal language providers. Zed does
not gain native JSON/YAML manifest-buffer attachment from this TOML registration.

## Database and evolution

SQLite table help uses `sqlName`, `strict`, `withoutRowid`; SQLite view/trigger
help uses that engine's accepted arguments. PostgreSQL-only options do not leak
into SQLite. Column hover includes storage type, nullability and constraints.
Advanced PostgreSQL declarations, Pg/Sqlite/Sql/Options/PartitionBound constructors
and finite values follow the selected engine and role. This is offline authoring;
completion does not connect to a database or apply a migration.

An evolution file is checked by the dedicated evolution compiler. Select its
previous/current schemas explicitly; otherwise `ADB502` explains the unavailable
context. A misspelled evolution argument reports `ADB501`.

VS Code project settings:

```json
{
  "axiom.projects": {
    "file:///absolute/database/project": {
      "entry": "schema.acore",
      "evolution": {
        "previous": "previous.acore",
        "current": "schema.acore"
      }
    }
  }
}
```

In Zed put that same `projects` object inside
`lsp.acore-lsp.initialization_options`. `previous: "Empty"` selects an empty
baseline; relative `.acore` and compatible `.axiom` baselines are captured locally.
Optional `previousSha256` / `currentSha256` pin compiled contract digests.
`history: {"path": "history.json", "sha256": "<64 lowercase hex characters>"}`
binds exact captured history bytes. This is not history-chain or deployment
validation; use the owning CLI for those explicit checks. Missing/stale selected
inputs produce diagnostics and suppress semantic navigation. Physical source
baselines support definition navigation; a compiled baseline has no invented
source location. Evolution formatting reparses in the evolution role.

## Backend and frontend bindings

Managed `perform` / `invoke` names, relative resource operations, `Input.*` and
`Steps.*` use compiler identities for hover, definitions, references and validated
rename. Current frontend component callbacks, primitive properties/methods,
String/List members, stores, form models and route/workflow references use typed
metadata. Navigation covers selected store/form/route bindings and migration
`old` scopes, including captured closed imports.

Within a `form_model` field, `raw` is a `String` input and `value` has that
field's declared type. Hover `raw` or `trim` in `raw.trim()` for typed help;
completion after `raw.` offers the checked String members, including `trim`,
`lower`, `upper`, `length` and `contains`. These inputs stay scoped to the field.

Rename returns versioned edits for open buffers and compiles the candidate before
accepting it. Repair diagnostics first. A collision, stale snapshot, unsupported
structural record/form key or unresolved consumer is rejected. This does not add
arbitrary record-field renaming or make generated/builtin declarations editable.

Style completion uses the accepted Acore stylesheet grammar and the intersection
of selected targets. Primitive properties, events and element methods are filtered
by compiler support; hover records registry status and upstream provenance.
Unknown stylesheet properties receive no broad fallback list. Upstream renderer
support alone does not imply an accepted Acore property.

## Thirteen checked starters

| Prefix | Profile / prerequisite |
| --- | --- |
| `acore-config` | Detached configuration |
| `acore-backend` | Backend `AxiomDeps.toml` |
| `acore-frontend` | Frontend manifest and entry/target selection |
| `acore-database` | PostgreSQL database manifest; select the entry |
| `acore-sqlite` | SQLite database manifest; select the entry |
| `acore-postgres-advanced` | PostgreSQL advanced declarations |
| `acore-evolution` | Database owner and explicit previous/current selection |
| `acore-security` | Backend audiences declared in the manifest |
| `acore-managed` | Backend managed composition |
| `acore-component` | Frontend component/event callbacks |
| `acore-store` | Frontend stores and migration |
| `acore-routes` | Frontend named routes |
| `acore-application-suite` | Frontend v6, compatible locked backend operations |

The default expansions are compiled through the real native server in their
selected profiles. `../examples/authoring` contains those expanded sources. The
application companion contains public backend source and frontend manifests;
build that backend and resolve its UI contract lock before checking the frontend.
No compiler executable or private runtime artifact is included in these examples.

TextMate and Tree-sitter cover the current contextual forms, nested calls and
named declarations with semantic tokens off. Compiler semantic tokens add typed
bindings when enabled. These words remain contextual syntax, rather than becoming
globally reserved names.

## Validation and remaining work

Native, grammar, adapter and installed VS Code provider checks pass on Apple
Silicon macOS with VS Code 1.105.1 and Zed 1.22.0. Keyboard hover and syntax with
semantic tokens off/on were visibly inspected in both editors, including the
final `form_model` documentation and full token range. Recorded Zed UI checks
also include completion insertion, signatures, diagnostics, recovery and rename.
Intel macOS, Linux, Windows and hosted Actions validation remain pending for this
candidate. L7 private artifact authoring, L8 graph/impact expansion, L9 later CLI
workflow implementations are covered by L7–L9; other-platform promotion remains deferred. Zed
still has no graph panel, type-hierarchy UI or virtual library/SDK/contract view.
Configuration hints/hierarchy are not generalized to all domain profiles.
