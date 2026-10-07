# Publication gates

**Release update (7 October 2026):** native LSP 0.1.0/0.1.1 downloads are withdrawn. Do not install or redistribute them; see [release status](RELEASE-STATUS.md). References below describe historical acceptance, not a currently available native release.

The adapter is Apache-2.0 by owner choice. The reviewed adapter/grammar
source is public. The owner subsequently approved the Mac native ZIP at
[withdrawn native release](RELEASE-STATUS.md).
The Z6 automatic installer remains disabled in adapter v0.1.3; use the public
ZIP with explicit path/PATH selection. See
[distribution preparation](DISTRIBUTION.md).

Prepare a clean adapter repository containing only Rust adapter/settings
code, manifests, queries, snippets, public examples, documentation, notices
and build checks. Keep the grammar's syntax parser and Apache-2.0 notices in
its separate clean repository. Review both contents and Git history. Exclude
`.local`, compiler/runtime source, source archives, binaries, internal evidence,
credentials and private fixtures. The existing `acore-vscode` validation
history must remain private.

The adapter/grammar Apache-2.0 license is separate from the proprietary native
compiler. The public Mac ZIP supplies the accepted executable, trusted digests,
compatibility manifest, native notice and conservative dependency notice
inventory. Native implementation source remains private. Signing/notarization
and recipient-machine Gatekeeper acceptance remain pending. The extension
must locate/download the server; it must not bundle an executable. The native
release records licensing/dependency metadata and signing status.
Digest-bound platform selection, cache recovery and offline reuse are implemented
in the adapter, but no automatic release is enabled. Enabling a raw-executable
download requires a separately reviewed manifest; the existing ZIP is a manual
installation route. A public grammar reveals Acore syntax; public native binaries
are also inspectable.
[Publishing prerequisites](https://zed.dev/docs/extensions/publishing/prerequisites),
[license requirements](https://zed.dev/docs/extensions/publishing/license-requirements).

The public adapter is **v0.1.3**; its manifest pins the new reviewed grammar
revision. The compatible Mac native release is **0.1.1**. These versions are
independent. Use the tested public adapter revision for the registry submission
and disclose manual ZIP/path native installation and the pending host gates.
Recheck that extension ID `acore` is available. Fork `zed-industries/extensions`,
add the adapter as an HTTPS submodule at `extensions/acore`, add the matching
version in `extensions.toml`, run `pnpm sort-extensions`, and prepare the
registry PR. Test a clean registry installation after its review and merge.
[Publishing guide](https://zed.dev/docs/extensions/publishing/publishing-guide).

Only the adapter/grammar need a public-source build workflow. Native compiler
builds remain a separate private/local pipeline. Actions billing recovery is
not required for local macOS development; other OS acceptance remains pending
under the owner's earlier instruction.

The prepared `.github/workflows/public-checks.yml` builds only the adapter/WASI
component, task checks and publicly pinned grammar. It never checks out native
compiler/runtime repositories or uploads captured source. The initial public-source run passed; a runner build does not certify a Linux
Zed desktop client. Local macOS acceptance remains a separate recorded result.

## Human registry submission

The current registry [AI policy](https://github.com/zed-industries/extensions/blob/main/AI_POLICY.md)
requires a human who understands the extension to submit its PR and write the
body/responses in their own words; autonomous agents may not contribute. Local
preparation and review do not constitute registry publication. A prepared patch
must be reviewed and submitted by the maintainer. Do not copy an AI-generated
PR body or maintainer response.

Use the release facts and tested commit as evidence, describe the extension in
your own words, and disclose its platform and native distribution limits.
Install the exact submission commit as a dev extension before submitting. After
merge, test a clean registry package. [MAINTENANCE.md](MAINTENANCE.md) explains
subsequent updates, version bumps and rollback.
