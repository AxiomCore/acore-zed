# Foreign interfaces and native language tooling

Acore uses captured SDK interfaces and explicitly refreshed native extraction.
The native implementation remains a Rust, TypeScript, Python or Go file, owned
by its existing Zed language provider. The Acore adapter registers only Acore;
it does not install, replace or reconfigure those providers. Core Acore editing
does not require the CLI or a native language provider.

## Prepare an authored extension's IDE helpers

Save and review the owning `AxiomDeps.toml` and native source. Inspect the CLI's
supported surface first:

```sh
axiom extensions interface --help
axiom extensions prepare-ide --help
```

If no reviewed canonical interface is available, emit the existing
manifest-generated SDK interface explicitly:

```sh
axiom extensions interface guest --deps "/path/to/owner/AxiomDeps.toml" --out "/path/to/owner/interface.json"
```

Then prepare physical IDE helpers from the reviewed interface:

```sh
axiom extensions prepare-ide guest --deps "/path/to/owner/AxiomDeps.toml" --interface "/path/to/owner/interface.json" --json
```

Replace `guest` with the declared alias. Omitting `--interface` selects the CLI's
manifest-generated ABI; do not assume it infers the implementation's exact
business types. Preparation writes `.axiom/extensions/ide/<alias>/`, including
a digest-bound receipt and physical Rust/TypeScript/Python/Go contract helpers.
The result records `executesGuest: false` and `authorityGranted: false`.
Preparation does not compile/run a guest, grant authority, prove runtime ABI
conformance or install a native provider. Existing `Cargo.toml`, `tsconfig.json`,
`pyrightconfig.json` and `go.mod` are not replaced.

[foreign-tasks.json](../templates/foreign-tasks.json) provides separate emission
and preparation tasks. Set `ACORE_ALIAS`, `ACORE_DEPS`, `ACORE_INTERFACE`, CLI path
and `cwd` to the correct owner. Both tasks use saved files and run only through
**task: spawn**. Review output changes; interface emission can overwrite the
selected output. Keep generated caches/helpers out of an unintended public
source release.

Open the authored Acore foreign binding and inspect hover/signatures after
preparation. The server reports the prepared signature and interface digest.
A changed native source, interface, manifest or helper can make the receipt
stale. Save intended changes, emit/review the interface as needed and explicitly
prepare again. Trigger a fresh hover or restart the Acore language server if the
editor still displays old state. A prepared receipt is not an execution or trust
grant. Zed has no read-only SDK virtual-document provider; this adapter suppresses
virtual definition targets. Open physical generated helpers directly.

## Refresh Go or FastAPI extraction

An Acore entry can use existing `axiom-go:` or `axiom-fastapi:` imports. Editing
shows missing/stale captured inputs instead of running their extractors. The
adapter always initializes effectful LSP RPCs with `workspaceTrusted: false`.
Use the existing CLI command deliberately after reviewing saved source and tools:

```sh
axiom editor refresh-extraction --help
axiom editor refresh-extraction --root "/path/to/owner" --entry "/path/to/owner/main.acore" --kind config --json
```

This invokes the declared native extractors and writes the fenced extraction
cache at `.axiom/interfaces/extracted.json`. It differs from `editor check`,
which consumes saved captures without executing extractors. Use the owning kind,
entry and variant supported by CLI help. Configure the approved extractor through
your existing environment (`AXIOM_GO_EXTRACTOR` / `AXIOM_FASTAPI_EXTRACTOR` where
used); task `env` accepts literal tool paths. Installing tools/dependencies is
separate. Extractors are native programs and can execute their own toolchain;
passive editing does not authorize them.

Use a CLI built with the same `compilerVersion` as the selected `acore-lsp`.
Z5 caught and retained evidence of the earlier CLI's cache being rejected after
the Z4 server changed its source fingerprint. A matched build fixes reuse
without weakening the cache's identity, source or tool digest checks. After
changing builds, refresh explicitly; do not edit the cache identity by hand.

The refresh task in [foreign-tasks.json](../templates/foreign-tasks.json) uses
`ACORE_PROJECT_ROOT` and `ACORE_ENTRY`. Pin both to a nested owner when needed.
The CLI reports its result and exit code in Zed's terminal. Missing/malformed
tools or invalid saved inputs fail visibly. Saving a changed native input makes
an old capture stale; explicit refresh updates its source/tool digests. Returning
to hover/completion or restarting analysis does not refresh extraction.

## Use the physical implementation's provider

Open native source and generated helpers as their normal languages. Configure
imports, Python stub paths, TypeScript declaration includes, Rust module paths
or Go modules in the owning native project's existing configuration as required
by that provider. Inspect the generated receipt/layout before choosing paths;
do not rename projected artifacts or substitute them for authored code.

On this Mac, Z5 acceptance observes TypeScript completion/hover/definition from
Zed's existing `vtsls` provider while Acore SDK hover remains available. Rust,
Python and Go files retain their identities and send no Acore `didOpen`. Their
full provider/toolchain typing is not certified by this phase. The extraction
acceptance uses declared local fixture tools producing the maintained Go/FastAPI
IR, not a production Go or FastAPI toolchain certification. Prepared helpers
provide captured contract types, with the native/runtime limits above.
Those ordinary providers retain their own discovery, download, indexing and
checking behavior. The Rust fixture has no Cargo workspace, so rust-analyzer
reports that workspace limitation; no Rust compilation acceptance is claimed.

See [CLI tasks and saved inputs](CLI.md), [settings and trust](SETTINGS.md) and
[feature limits](FEATURES.md). Acceptance is macOS ARM64 only. Other operating
systems and public distribution remain later release gates.
