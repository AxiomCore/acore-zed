# Install Acore for Zed

Zed adapter **0.1.5** pins corrected native LSP **0.1.2** for macOS ARM64.
LSP 0.1.0 and 0.1.1 are withdrawn; see [release status](RELEASE-STATUS.md).
Other platforms and registry installation remain pending.

## Install the public source locally

```sh
git clone --branch v0.1.5 https://github.com/AxiomCore/acore-zed.git
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

Automatic installation downloads the immutable 0.1.2 macOS ARM64 executable
when no explicit path or PATH server is selected. It verifies SHA-256, size and
protocol/compiler metadata before activating the cache. A stale or corrupt cache
is rejected; a failed download does not restore a withdrawn version.

For a manual or offline installation, obtain these assets from the
[0.1.2 release](https://github.com/AxiomCore/AxiomCore/releases/tag/acore-lsp-v0.1.2):
`acore-lsp-macos-arm64.zip`, `acore-lsp-release.json` and `SHA256SUMS`. Verify the
ZIP against SHA256SUMS, extract into a new directory, and verify the executable
against `native.sha256` in the release manifest. Its SHA-256 must be
`911c7da384b2ea9b60be7171e218b6bdfabdd2b90073ab1cc1f4a891d7324030`.
Keep NATIVE-NOTICE.txt and third-party-notices with the executable. Run
`./acore-lsp --version-json`; the server version must be `acore/0.1.2 (E7)` and
the compiler identity must match the release manifest. An old archive is unsafe
even when its historical checksum matches.

Ad-hoc signing is verified on the acceptance host. Developer ID notarization and
recipient-machine Gatekeeper acceptance are not certified. Obtain an approved
signed build if required by your system; do not bypass operating-system checks.

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
the same `compilerVersion`; use the matching public CLI 0.148.1 release. See [WORKFLOWS.md](WORKFLOWS.md).

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
language server. Keep only verified, supported native versions for rollback. Withdrawn versions are not rollback candidates. A standalone
Cargo build alone does not update Zed's installed component. Same-session rebuilds
can duplicate snippet registrations; save work and restart Zed if affected.

After registry approval, developers can search **Acore** in Zed's Extensions page.
Remove a dev override before testing the registry package; this installation
route is still pending. See [MAINTENANCE.md](MAINTENANCE.md) for future releases.
