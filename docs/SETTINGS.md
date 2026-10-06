# Acore settings

Put the server override in user settings or the owning project's
`.zed/settings.json`. Project settings remain subject to Zed's worktree trust
controls. The adapter uses the configured path first, then the worktree PATH, then its
compiled approved release/cache;
it preserves configured arguments and environment without constructing a shell
command. The initial source release keeps automatic public downloads disabled pending
asset promotion. See [distribution and recovery](DISTRIBUTION.md).

Before LSP initialization, the adapter invokes the selected executable with
`--version-json`. It requires an `acore/…` server identity, editor protocol
`axiom-editor/v1`, a valid compiler fingerprint, and
`editorFeatures.virtualDocumentNavigationOptOut: true`. Use the Z4-compatible
native server; older E7 builds do not implement this presentation safeguard.
Different compatible compiler builds are allowed; this checks compatibility, not binary provenance.
Missing, non-executable and wrong-format paths also produce host startup errors.
Use the maintainer's SHA-256 receipt to check the native artifact separately.

Version metadata is a separate invocation, without the stdio arguments.
Wrappers must implement `--version-json` by themselves. Runtime arguments and
environment remain literal. Relative override paths resolve from the worktree
root; absolute paths are recommended. The metadata query inherits the worktree
shell environment plus the configured environment. Zed's process API provides
no per-query timeout; an executable that hangs in its version interface can
stall startup. Use the supplied standalone server.

```json
{
  "lsp": {
    "acore-lsp": {
      "binary": { "path": "/absolute/path/to/acore-lsp" },
      "initialization_options": {
        "frontend": { "entry": "main.acore", "targets": ["web"] },
        "database": { "entry": "schema.acore" }
      }
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

The frontend/database selection options apply to their respective project
owners; omit them when defaults select the correct entry. Other existing
native settings include `configurationFiles` and the `projects` map keyed by
project root URI. `configurationFiles` maps patterns to manifest kinds such as
`"deps"` or `"extension-workflow"`, rather than encoding names such as `"toml"`.
They refine server ownership/analysis. The adapter already registers Acore and
TOML; associations select recognized inputs within that registration, rather
than creating a replacement language. Initialization options must be an object.

`lsp.acore-lsp.settings` supplies live overrides through
`workspace/didChangeConfiguration`. The adapter starts with the initialization
selections and merges explicit live values recursively: objects merge, arrays
replace, and `null` clears an optional field. Removing an override restores its
initialization value. An empty live object retains the initialization selections.
This matters because Zed sends a live update immediately after initialization
and the native server replaces its editor configuration with that payload.
Use flat native fields as in `initialization_options`; an `axiom` wrapper is also
normalized while preserving its shape for the host's final merge. Trust cannot
be granted through either settings surface. The adapter also supplies
`virtualDocumentNavigation: false` during initialization and rejects attempts
to enable it through startup/live settings. This session option prevents
virtual URIs from becoming editable filesystem buffers in the tested host.
It does not remove SDK hover, physical navigation or native projection services.

Startup settings need a restart. Z3 passed **editor: restart language server**
in Zed 1.22.0, including reattachment of existing buffers with unsaved edits in
all four profiles, Unicode and physical imports. A tested initialization-selection
change also started a replacement process and resynchronized the open buffers.
Zed 1.21.0 had failed automatic reattachment in the earlier Z2 test. After
changing startup settings, use the restart action with an Acore file active and
confirm diagnostics/completion resume. If authoring remains disconnected, reopen
the project in a new Zed window. Other startup-change combinations are not
certified merely by a replacement process starting.

The adapter defaults to `workspaceTrusted: false` because the reviewed public
extension API has no worktree-trust accessor. It rejects a supplied value other
than `false`: Zed merges user overrides after the adapter hook, so replacing an
unsafe value in the returned object alone cannot enforce the restriction.
Ordinary offline editing is
available. Evaluation, dependency resolution and extraction through execution
RPCs remain disabled; invoke the CLI explicitly for those workflows. Setting
that flag to true produces an actionable startup error. Zed Restricted Mode
continues to govern whether the project server and version query can run.

Adapter 0.1.3 registers the native server for Acore, existing TOML and JSON. Keep
`AxiomDeps.toml` in TOML: recognized manifests receive Axiom completion/hover and
unsaved overlays, while ordinary TOML receives no Axiom authoring services.
Existing TOML language servers may remain enabled through Zed's normal per-language
selection. Recognized private JSON inputs also receive native assistance; ordinary
JSON receives no Acore authoring response and retains its normal provider. YAML/Pkl
keep their existing providers. See [private JSON/workflows](WORKFLOWS.md).
See [L1–L6 authoring](AUTHORING.md) for explicit evolution selections and the
thirteen starters. Semantic tokens supplement Tree-sitter colors when `combined`
is enabled. [Zed language settings](https://zed.dev/docs/configuring-languages),
[semantic highlighting](https://zed.dev/docs/extensions/languages).
