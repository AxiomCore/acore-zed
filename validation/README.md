# Local validation and release

Builds, checks and artifact uploads are owned by the local release cycle.
GitHub Actions is reserved for SDK publication; push, pull-request, scheduled
and release-tag CI jobs are disabled.

Run release operations from the sibling private `Axiom-release-plane` checkout:

```sh
just release containers
just release web
```

Useful repository checks:

```sh
cargo +1.93.0 test --locked --lib
cargo +1.93.0 build --locked --release --target wasm32-wasip2
python3.12 scripts/check-tasks.py
python3.12 scripts/check-grammar.py
python3.12 tests/test_release_tools.py
```

`former-github-actions/` preserves the previous command recipes for reference;
these files are outside GitHub's workflow directory and cannot start Actions.
Setup steps and GitHub expressions in those recipes are historical, not a
local execution interface. Use the commands above and the controller's operator guide. Native/editor acceptance on this Mac covers macOS ARM64;
Windows and other host-platform qualification must run on those platforms.
Upstream Lynx qualification remains available through the private controller's
qualification scripts when evaluating a new engine version.
