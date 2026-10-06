# Test Acore for Zed

The accepted host is Apple Silicon macOS 26.2, Zed 1.22.0, Rust 1.93.0 and
Tree-sitter CLI 0.25.4. Other operating systems and physical Intel Macs remain
pending. Native protocol checks and a WASI build do not certify another Zed host.

## Source checks

Keep the adapter and grammar checkouts beside each other. Python 3.11 or later
is required by the helpers. Run from the adapter:

```sh
cargo +1.93.0 test --locked --lib
cargo +1.93.0 clippy --locked --all-targets -- -D warnings
cargo +1.93.0 build --locked --release --target wasm32-wasip2
(cd ../tree-sitter-acore && tree-sitter test)
python3 scripts/check-grammar.py
python3 scripts/check-tasks.py
python3 tests/test_release_tools.py
```

The grammar helper checks the adapter queries and
incomplete-input/Unicode/CRLF recovery. Task checks exercise quoting, paths,
saved input selection and missing-tool behavior. The public CI workflow runs
source checks only; it does not build the proprietary compiler or claim desktop
acceptance on its runner.

## Real native smoke check

Obtain a compatible native server and its trusted SHA-256 from the maintainer.
Confirm the host architecture and metadata. Substitute the supplied digest:

```sh
file /absolute/path/to/acore-lsp
shasum -a 256 /absolute/path/to/acore-lsp
/absolute/path/to/acore-lsp --version-json
python3 scripts/smoke-server.py \
  --server /absolute/path/to/acore-lsp \
  --expected-sha256 THE_MAINTAINER_SHA256 \
  --output smoke-results.json
```

The smoke helper checks the digest before executing the server, then checks all
four public examples using real framed stdio. It verifies clean diagnostics,
typed hover, completion, semantic tokens, unsaved invalidation and recovery.
It uses temporary copies, disables trust and virtual navigation, and confirms
saved inputs were not changed. It does not emulate or certify Zed's UI. No CLI,
runtime, network dependency resolver, extractor or database is invoked.

## Real Zed acceptance

1. Install the dev extension using [INSTALL.md](INSTALL.md). Open a disposable
   copy of [examples](../examples/README.md) as a worktree and configure the
   compatible server using [SETTINGS.md](SETTINGS.md).
2. Open each profile. Confirm **Acore** in the status bar, syntax colors,
   outline, bracket matching, indentation, snippets and compiler hover.
3. In configuration, replace `flag`'s Boolean with a string. Confirm the error
   appears before saving, undo and confirm it clears. Enable inlay hints and
   check `count: Int`. Navigate `Settings` to `types.acore`.
4. In backend, hover/navigate the model; in frontend, complete `increment` at
   `on_press`; in database, complete `DatabaseEngine` members and inspect the
   `title` declaration. No database connection should be needed.
5. Follow [TYPED_EDITING.md](TYPED_EDITING.md) for signatures, references,
   workspace symbols, validated symbol rename, quick fixes, formatting and
   Unicode/CRLF. Follow [E7_CONFIGURATION.md](E7_CONFIGURATION.md) for hints,
   manifest coexistence and the configuration file-rename limitation.
6. Leave an edit unsaved and run **editor: restart language server**. Confirm
   text survives and diagnostics/completion resume. Save and compare an explicit
   CLI check only when you intend to check the saved version.
7. Use [CLI.md](CLI.md) for optional project-local tasks and
   [FOREIGN_WORKFLOWS.md](FOREIGN_WORKFLOWS.md) for explicit extraction/SDK work.
   Missing tools must report a terminal error without disabling the LSP.

Keep test changes in disposable projects. Review returned multi-file edits
before saving. A rejected configuration file refactor does not stop Zed moving
the file; repair errors first and review imports afterward. Type hierarchy,
typed manifest buffers, virtual documents and graph panels have no supported
Zed surface; see [FEATURES.md](FEATURES.md).

Use **zed: open log** for startup failures. A dev rebuild can reload other
worktrees' Acore servers; confirm they reconnect. Rebuilding can duplicate snippet
suggestions within the session. Save your work before a normal editor restart.

## Release verification

Install the exact tested public commit as a dev extension before submission.
After maintainers merge the registry PR, test the actual registry package:
remove the dev override through Zed's extension UI, install **Acore**, open a
fresh disposable worktree, and repeat the four-profile checks. Record the
extension/server hashes, Zed version, platform and settings. Verify the intended
server path or anonymous pinned download and offline restart; a Cargo exit code
alone cannot establish which component Zed loaded.

See [PERFORMANCE.md](PERFORMANCE.md) for measured limits and
[MAINTENANCE.md](MAINTENANCE.md) for update and rollback checks.
