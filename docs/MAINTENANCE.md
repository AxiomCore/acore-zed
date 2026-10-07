# Distribute, update and roll back Acore for Zed

**Release update (7 October 2026):** native LSP 0.1.0/0.1.1 downloads are withdrawn. Do not install or redistribute them; see [release status](RELEASE-STATUS.md). References below describe historical acceptance, not a currently available native release.

## Developer distribution

Before registry publication, share the adapter/grammar Git checkouts or their
reviewed source archives and a separately supplied compatible server. Follow
[INSTALL.md](INSTALL.md) for dev installation. Private native server access is
independent of an Apache-2.0 adapter checkout. Never share the private compiler
capture repository/history as an extension package.

The public repositories now exist; developers can clone their reviewed tags,
or use Zed's **Extensions** page after the registry submission is merged and
packaged. Search for **Acore** and install it. No VSIX upload is used.
An installed dev extension overrides the registry package; remove that override
through Zed's UI before testing registry installation.
[Zed publication](https://zed.dev/docs/extensions/publishing/publishing-guide).

The adapter selects an explicit server path, then worktree PATH, then its
compiled active release. If no public release is enabled or the execution host
has no approved artifact, developers must obtain a compatible server from the
maintainer and configure its path. A public adapter does not by itself publish
or license the compiler. See [DISTRIBUTION.md](DISTRIBUTION.md).

## Release an adapter or grammar update

Work from a clone of the public repository and preserve its history. Do not push
the private validation workspace or regenerate a fresh public root for updates.
Copy only reviewed source changes when development happens in that workspace.


1. Make the change in its owning layer; see [ARCHITECTURE.md](ARCHITECTURE.md).
   For grammar changes, commit the generated parser, pass corpus/query tests,
   publish its exact commit and update `grammars.acore.rev` in `extension.toml`.
2. Increase the adapter version in `extension.toml` and `Cargo.toml`, update
   Cargo.lock through Cargo, and add a changelog entry. Do not overwrite a
   reviewed tag or immutable native release asset.
3. Run [TESTING.md](TESTING.md). Install the exact candidate commit as a dev
   extension in actual Zed. Record hashes, settings, host/version and limitations.
4. Commit/push the reviewed public branch, tag that exact commit, and retain the
   release receipts. A tag alone does not update the Zed registry.
5. In a personal fork of `zed-industries/extensions`, update only
   `extensions/acore` to that exact public commit and match its version in the
   root `extensions.toml`. Sort and inspect the diff:

   ```sh
   git -C extensions/acore fetch origin
   git -C extensions/acore checkout THE_TESTED_PUBLIC_COMMIT
   # Edit only [acore].version in extensions.toml to the adapter version.
   pnpm sort-extensions
   git add .gitmodules extensions.toml extensions/acore
   git diff --cached --stat
   ```

6. A human maintainer must write and submit the update PR and review responses
   in their own words under the registry [AI policy](https://github.com/zed-industries/extensions/blob/main/AI_POLICY.md).
   Repeat clean registry installation
   after maintainers merge/package it. Developers then update through Zed's
   Extensions UI according to their update settings.
[Zed update process](https://zed.dev/docs/extensions/publishing/updating-and-maintenance).

Use an exact tested commit, rather than accepting whatever a moving remote
branch currently points at. Keep the commit reachable from the published branch.
Each registry PR must add/update one extension; respond to maintainer feedback
within three weeks. Public source checks never need a token for the private
native compiler repositories.

## Release a native compiler/server update

The compatible Mac server is published separately in
[withdrawn native release](RELEASE-STATUS.md).
Build and test native changes privately, then use the release dashboard's
**Acore LSP** component to publish a new immutable ZIP, compatibility manifest
and checksums. Source remains private. Supply the matching optional CLI when
its compiler fingerprint changes. Developers verify the assets, extract the
ZIP, select the new executable through `lsp.acore-lsp.binary.path` and restart.
A server upload does not update the adapter or its compiled release pins.

Keep `releases/server.json` disabled for this manual ZIP route. Enabling
public automatic native downloads remains a separate adapter change: review
platform identities, final-byte notices/terms and signing acceptance, publish
installer-compatible assets, verify anonymous downloads, then update the
compiled release ID, platform URLs and digests and bump the adapter version.
The current installer expects a raw executable, so do not pin the ZIP URL as
though it were the executable. Other platforms remain pending until their
own artifact and desktop acceptance pass.

If the compiler fingerprint changes, supply the matching optional CLI and
refresh extraction explicitly before expecting the LSP to reuse its cache.
Repeat relevant shared VS Code/native regressions as well as Zed acceptance.

## Rollback

For an immediate developer rollback, select a reviewed compatible earlier
executable using `lsp.acore-lsp.binary.path` and restart the language server.
Version/hash caches are retained; valid old bytes work offline. Do not bypass
hash verification or silently substitute an old server for a failed new pin.

For a registry rollback, publish a **new higher adapter version** pointing at
the previously reviewed server/grammar configuration, test it and submit an
update PR. Do not mutate existing release assets or force-move tags. See
[DISTRIBUTION.md](DISTRIBUTION.md) for corrupt cache and missing asset recovery.
