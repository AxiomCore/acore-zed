# Publication gates

The adapter is Apache-2.0 by owner choice. The working manifest's public
URLs are populated in the clean source export, and no public native download
is enabled until redistribution is approved. Z6 provides a verified installer and clean one-commit source exports. Public
activation/promotion remains a reviewed release action. See
[distribution preparation](DISTRIBUTION.md).

Prepare a clean adapter repository containing only Rust adapter/settings
code, manifests, queries, snippets, public examples, documentation, notices
and build checks. Keep the grammar's syntax parser and Apache-2.0 notices in
its separate clean repository. Review both contents and Git history. Exclude
`.local`, compiler/runtime source, source archives, binaries, internal evidence,
credentials and private fixtures. The existing `acore-vscode` validation
history must remain private.

The owner selected Apache-2.0 for the adapter. The owner selected private native binary delivery for the initial release.
Supply authorized developers a compatible executable, trusted digest and separate
terms/notices. Public native redistribution remains a separate future approval
and notice/signing review; any approved public assets need their own immutable
release manifest. The extension
must locate/download the server; it must not bundle an executable. The release candidate records
binary licensing/dependency metadata and signing status. Digest-bound platform
selection, cache recovery and offline reuse are implemented; licensing/notices,
public activation and signing policy remain owner review gates. A public grammar reveals Acore syntax;
public native binaries are also inspectable.
[Publishing prerequisites](https://zed.dev/docs/extensions/publishing/prerequisites),
[license requirements](https://zed.dev/docs/extensions/publishing/license-requirements).

The reviewed adapter and grammar v0.1.0 source releases are public. Their HTTPS
URLs and grammar revision are pinned, and the exact tagged adapter has passed
macOS dev installation. No native executable was uploaded. Prepare registry
submission using the tested public revision and private-server instructions.
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
