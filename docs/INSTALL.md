# Install Acore for Zed

The Apache-2.0 adapter and grammar can be installed from their reviewed source
release. Download the compatible Mac native server from
[Acore LSP 0.1.0](https://github.com/AxiomCore/AxiomCore/releases/tag/acore-lsp-v0.1.0).
Registry installation and automatic native downloading remain pending. The
ZIP is used through explicit path/PATH selection; the adapter
`releases/server.json` still has `activeRelease: null`.

## From Git

Use the reviewed public source tags:

```sh
git clone --branch v0.1.1 https://github.com/AxiomCore/acore-zed.git
git clone --branch v0.1.0 https://github.com/AxiomCore/tree-sitter-acore.git
cd acore-zed
```

The server is supplied separately; source checkout access alone does not supply
it. A team may also share these same reviewed sources through private Git.

## From the source checkout

Keep `acore-zed` and `tree-sitter-acore` beside one another. Install Rust through rustup and Tree-sitter CLI
0.25.4. From `acore-zed`:

```sh
rustup toolchain install 1.93.0 --profile minimal
rustup target add wasm32-wasip2 --toolchain 1.93.0
cargo +1.93.0 test --locked --lib
cargo +1.93.0 build --locked --release --target wasm32-wasip2
python3 scripts/check-grammar.py
python3 scripts/configure-dev.py
```

Run `tree-sitter test` from the sibling grammar checkout as well. The optional
`--examples ../axiom-frontend/apps/playground/src/examples` argument to
`check-grammar.py` also validates the local playground corpus.

The grammar checkout must be clean and committed. The helper pins its exact
revision in an ignored development copy and prints that copy's directory.
The published manifest pins the public grammar commit. The local helper
overrides that pin only in the ignored dev copy for local grammar testing.

In Zed, open the command palette, run **zed: install dev extension**, and
select the printed directory. Zed builds the Rust adapter and grammar; it can
download the grammar's WASI SDK automatically. When updating source, rerun
`configure-dev.py`, run **zed: rebuild dev extension**, and restart the language
server if its settings changed. A successful standalone Cargo build does not update Zed's installed
WebAssembly component. [Zed dev installation](https://zed.dev/docs/extensions/developing-extensions).

Zed 1.21.0 showed duplicate snippet suggestions after a same-session rebuild.
The manifest references each of the four snippets once; expansion and tab
stops still work. Zed's snippet registry appends entries on registration, and
extension reload does not remove them. A normal restart after saving your work
is expected to clear that session state; restart recovery was not performed
during acceptance because other user windows were open.
[Zed snippet registry](https://github.com/zed-industries/zed/blob/33c95853ed2b6956f339733c63a8220964ecbeb6/crates/snippet_provider/src/registry.rs).

## Select the native server

For Apple Silicon macOS, download all three release assets into an empty
folder and check the ZIP and metadata before extracting:

```sh
mkdir acore-lsp-0.1.0
cd acore-lsp-0.1.0
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.0/acore-lsp-macos-arm64.zip
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.0/acore-lsp-release.json
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.0/SHA256SUMS
shasum -a 256 -c SHA256SUMS
unzip acore-lsp-macos-arm64.zip
./acore-lsp --version-json
```

The accepted native SHA256 is
`1b668d5e0a2fcb94ee24e7aef1c575b876125e92253760c1f8d6838287a35847`.
Native distribution terms and dependency notices are in the ZIP. Signing,
notarization and recipient-machine Gatekeeper acceptance remain pending.
No security bypass is part of these installation steps.

Inspect the extracted binary before configuring it:

```sh
/absolute/path/to/acore-lsp --version-json
file /absolute/path/to/acore-lsp
shasum -a 256 /absolute/path/to/acore-lsp
```

Use the maintainer's recorded digest and host architecture. The current
protocol is `axiom-editor/v1`; Z4 also requires version metadata
`editorFeatures.virtualDocumentNavigationOptOut: true`. Obtain the matching
Z4 server as well as the adapter, because older E7 binaries are rejected.
Set `lsp.acore-lsp.binary.path` to the absolute
executable path in Zed settings, or install it as `acore-lsp` on the worktree
PATH. See [settings](SETTINGS.md). The CLI is optional for core editing.

## Verify the editor

Open a complete project and a `.acore` file. Confirm the status bar says
**Acore**, then check syntax coloring, compiler hover and diagnostics. For a
configuration project, start with:

```acore
class Settings { enabled: Boolean = true }
settings: Settings = Settings { enabled = false }
count = 42
```

Hover `Settings`; enable hints and check `count: Int`; change an explicitly
typed value to an incompatible string and check its diagnostic. Allow analysis
to finish before testing completion or navigation. Z1 syntax and Z2 native
connection acceptance and Z3 standard typed editing are complete on macOS
ARM64. Z3 used Zed 1.22.0 and passed the restart action with unsaved buffers.
Z4 E7/configuration compatibility is complete with the explicit host limits in
[E7_CONFIGURATION.md](E7_CONFIGURATION.md). After changing
startup settings, reopen the project in a new window if the server restart does
not reconnect the buffers. Follow the [typed-editing walkthrough](TYPED_EDITING.md)
and [feature guide](FEATURES.md) for the current evidence and limits.

Use **zed: open log** for startup failures. A missing server has an actionable
message. Check the configured path, permissions, architecture and version for
wrong-binary failures. The Z2 adapter validates
`--version-json` before initialization; [verified downloads and cache recovery](DISTRIBUTION.md)
are implemented, with public asset promotion pending.
See [connection troubleshooting](TROUBLESHOOTING.md) for the current errors and
recovery steps.

For maintainers updating an already installed dev extension from the terminal:

```sh
python3 scripts/build-dev.py
```

This builds the locked release WASI component and regenerates the pinned dev
copy. On this Mac, an installed out-of-tree dev symlink can be refreshed with:

```sh
python3 scripts/build-dev.py --installed-dev-link "$HOME/Library/Application Support/Zed/extensions/installed/acore"
```

The helper only refreshes a symlink that already points at the generated copy.
It does not install a new extension or change Zed settings/trust. The release
component retains its custom sections; Zed's own builder strips debug sections
when using **zed: rebuild dev extension**. First installation still uses the
Zed command. This terminal route is for private development, not registry
packaging.

macOS ARM64 release acceptance is complete for the supplied native candidate; Linux, Windows and physical Intel Mac acceptance are pending.

After registry publication, open Zed **Extensions**, search **Acore** and install.
Remove a dev override through Zed first when testing the registry package.
Follow [TESTING.md](TESTING.md) for the complete test sequence and
[MAINTENANCE.md](MAINTENANCE.md) for distribution and updates.
