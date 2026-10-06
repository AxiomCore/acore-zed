# Install Acore for Zed

Zed adapter **0.1.3** uses the public grammar pinned in `extension.toml` and
[Acore LSP 0.1.1](https://github.com/AxiomCore/AxiomCore/releases/tag/acore-lsp-v0.1.1).
This native release contains L1–L9. The historical 0.1.0 ZIP remains unchanged.
Apple Silicon macOS is validated; Intel macOS, Linux, Windows and remote desktop
acceptance remain pending. Registry installation awaits human submission and
maintainer merge. Automatic server downloads remain disabled.

## Install the public source locally

```sh
git clone --branch v0.1.3 https://github.com/AxiomCore/acore-zed.git
cd acore-zed
rustup toolchain install 1.93.0 --profile minimal
rustup target add wasm32-wasip2 --toolchain 1.93.0
```

In Zed run **zed: install dev extension**, and select this checkout directory
containing `extension.toml`. Zed builds the adapter and downloads/builds the exact
public grammar revision itself. The native compiler is supplied separately below.
Other developers can use the same Git URL/tag and installation action; no private
compiler source checkout is needed. The Apache-2.0 adapter/grammar licenses do not
license the native compiler or optional CLI.

## Install and select the native server

For Apple Silicon macOS, download all three assets into a new directory:

```sh
mkdir acore-lsp-0.1.1
cd acore-lsp-0.1.1
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.1/acore-lsp-macos-arm64.zip
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.1/acore-lsp-release.json
curl -fLO https://github.com/AxiomCore/AxiomCore/releases/download/acore-lsp-v0.1.1/SHA256SUMS
shasum -a 256 -c SHA256SUMS
unzip acore-lsp-macos-arm64.zip
./acore-lsp --version-json
file ./acore-lsp
shasum -a 256 ./acore-lsp
```

The accepted executable SHA-256 is `582716716d1c72ef2de00c346e37868ee892bae71df34538493c9fa3814c0af7`.
Version metadata must report `acore/0.1.1 (E7)`, `axiom-editor/v1`,
`compilerVersion: dc94883ad55983d698a5141bd0e4230075365de549209a52949933d8bb563195`
and `editorFeatures.virtualDocumentNavigationOptOut: true`.
The ZIP includes separate proprietary terms and dependency notices.
Signing, notarization and recipient-machine Gatekeeper acceptance remain pending;
no security bypass is part of these steps.

Set an absolute executable path in Zed user settings:

```json
{
  "lsp": {"acore-lsp": {"binary": {"path": "/absolute/path/to/acore-lsp"}}},
  "languages": {"Acore": {"semantic_tokens": "combined", "inlay_hints": {"enabled": true}}}
}
```

Alternatively install the verified executable as `acore-lsp` on the worktree PATH.
Run **editor: restart language server** after changing it. An explicit path takes
precedence over PATH. Verify that the intended process/version is selected; an
old executable can still speak the protocol while lacking the new features.
Core editing needs no CLI. Explicit tasks require a separately supplied CLI with
the same `compilerVersion`; use the private validated CLI until a matching CLI
release is available. See [WORKFLOWS.md](WORKFLOWS.md).

## Check the installed editor

Open one of the [four example projects](../examples/README.md). Check the Acore
language in the status bar, hover a declaration, insert a typed completion,
request a signature, introduce an unsaved type error and repair it. Repeat after
restarting the language server. In `AxiomDeps.toml`, check field documentation and
Audience values. In a frontend `form_model`, hover `raw` and `trim`, check typed
String member completion and contextual syntax coloring. Recognized private JSON
receives role help; ordinary JSON/TOML retains its normal providers.

Use **zed: open log** for startup failures. Missing paths, wrong permissions,
wrong architecture or incompatible metadata need the appropriate verified
executable. See [TESTING.md](TESTING.md), [FEATURES.md](FEATURES.md) and
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) for exact limits.

## Develop grammar or adapter changes

For optional local grammar work, clone the public grammar beside the adapter and
check out its exact `extension.toml` revision. With Tree-sitter CLI 0.25.4:

```sh
git clone https://github.com/AxiomCore/tree-sitter-acore.git ../tree-sitter-acore
git -C ../tree-sitter-acore checkout 39bfab9ded526cf141bfdc18416c92cd2bcfca1f
cargo +1.93.0 test --locked --release --lib
cargo +1.93.0 build --locked --release --target wasm32-wasip2
python3 scripts/check-grammar.py
python3 tests/test_release_tools.py
(cd ../tree-sitter-acore && tree-sitter test)
python3 scripts/configure-dev.py
```

The real CLI workflow tests additionally need `AXIOM_CLI_PATH` and
`ACORE_LSP_PATH` pointing to matching tools; then run
`python3 scripts/test-workflows.py`.

Install the printed development copy using Zed's dev extension action. For
updates, pull the new reviewed tag, rebuild the dev extension and restart the
language server. Keep the old checkout/native version for rollback. A standalone
Cargo build alone does not update Zed's installed component. Same-session rebuilds
can duplicate snippet registrations; save work and restart Zed if affected.

After registry approval, developers can search **Acore** in Zed's Extensions page.
Remove a dev override before testing the registry package; this installation
route is still pending. See [MAINTENANCE.md](MAINTENANCE.md) for future releases.
