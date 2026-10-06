# Verified server installation and recovery

The Z6 installer is implemented and locally accepted on macOS ARM64. The owner
selected public Apache-2.0 adapter/grammar source and private native delivery.
Registry installation remains pending human submission and maintainer merge.
`releases/server.json` deliberately has `activeRelease: null` in this release. With no explicit path or worktree PATH server, it reports that no approved
download release is enabled. Use a supplied verified server as documented in
[INSTALL.md](INSTALL.md). No GitHub token or private repository access is part
of the installer. The CLI remains separate and optional.

## Selection and integrity

Selection is explicit `lsp.acore-lsp.binary.path`, then worktree `acore-lsp` on
PATH, then the approved pinned release for the **execution host** from Zed's
platform API. An invalid explicit/PATH server fails; it does not silently select
a download. Configured arguments/environment remain literal. Overrides are
user-selected programs: verify their provenance using the maintainer's receipt.
Their version metadata is checked, but they are not asserted to match a release
hash. For downloaded/cached servers, the adapter verifies bytes itself.

The release manifest is compiled into the adapter, rather than downloaded from
`latest` or supplied by a worktree. Each release pins platform, raw executable
URL, exact size, SHA-256, server/protocol version and compiler fingerprint.
Streams are bounded by the pinned size (maximum 128 MiB). Downloads are written
to an exclusive partial file; checksum/size failure, transfer error or permission
failure prevents promotion and execution. Persisted bytes are checked again
after executable permissions are applied, then renamed atomically into place.
Raw executable assets avoid archive unpacking and archive path traversal.

The cache is below Zed's Acore extension work directory:

```text
servers/<release-id>/<platform>/<sha256>/acore-lsp
```

Windows would use `acore-lsp.exe`; no Windows artifact or acceptance is supplied
by this phase. The installed Mac cache file is separate from extension.wasm and
is not bundled in extension source. Every selection rechecks its SHA-256 and
size before a metadata query or LSP launch; no receipt's `verified` flag is
trusted. Cache file/directory symlinks are rejected. Valid cached bytes can be
reused entirely offline; executable permissions are repaired through Zed's API.
The shared server's effectful RPCs remain `workspaceTrusted: false`.

Zed's HTTP stream API does not expose the response status in the guest. A missing asset
can return an HTTP error body through this API; it is rejected by exact
digest/size just like a corrupt or truncated asset. Network errors also fail.
There is no download timeout parameter in this API. Host cancellation and a hard
process interruption can leave an unused partial file; it is never a server and
a fresh attempt uses an exclusive filename. Normal errors clean up their partial.
[Zed HTTP API contract](https://github.com/zed-industries/zed/blob/76659a55a8c10ed355a070f8764a0b1733e3c115/crates/extension_api/wit/since_v0.6.0/http-client.wit).

## Update, rollback and offline use

An extension update can change the compiled active release. Each version/hash
has a separate cache path. Successful updates retain earlier caches. A failed
new download does not run corrupt bytes or silently launch an old version;
select a reviewed prior executable with `binary.path` or restore the approved
older adapter release, then restart the Acore language server. This also works
offline. Changing the compiler may require explicit CLI extraction refresh with
a matching CLI; see [foreign workflows](FOREIGN_WORKFLOWS.md).

| Failure | Recovery |
| --- | --- |
| No approved release enabled | Supply the separately delivered verified standalone path/PATH server. |
| No approved asset for the host | Supply a compatible reviewed binary. macOS ARM64 is accepted; other hosts remain pending. |
| Missing asset / network unavailable | Retry the exact release after connectivity is restored, or use a verified offline override/cache. |
| Download size/SHA-256 mismatch | Do not run the partial/corrupt file. Retry the pinned release; ask the maintainer to repair the distribution without changing the pin silently. |
| Corrupt existing cache while offline | It is rejected. Restore the exact approved bytes or use a verified prior path. A successful online retry replaces it only after verification. |
| Permission/symlink cache error | Correct permissions on the reviewed cache, or remove the unexpected cache link and retry. Do not disable checksum checks. |
| Startup remains disconnected | Use **editor: restart language server** from an Acore buffer; reopen the project if reattachment fails. |

## Maintainer release preparation

From the adapter checkout, package the final reviewed standalone Mac executable:

```sh
python3 scripts/package-server.py --binary /path/to/acore-lsp \
  --expected-sha256 <digest-from-trusted-build-receipt> \
  --release-id <immutable-release-id> \
  --asset-base-url https://github.com/AxiomCore/acore-lsp-releases/releases/download/<immutable-release-id> \
  --output .local/server-candidate
```

The URL above is a proposed assets-only route, not an existing published release.
The helper checks the trusted digest **before** invoking `--version-json`, checks
Mac ARM64 format and metadata, and writes the raw asset, SHA256SUMS, release pins
and a distribution-review notice. It does not build private sources or upload.
The native terms/notices and signing/notarization policy need owner review. The
current Mac artifact is linker ad-hoc signed, with no Developer ID/notarization
acceptance. Signing or stripping changes bytes: regenerate the candidate and
pins from the final artifact. Do not instruct developers to bypass Gatekeeper.

Prepare fresh local source repositories from the explicit allowlists:

```sh
python3 scripts/prepare-public.py --output .local/public-candidate \
  --release-pins .local/server-candidate/server.json
python3 scripts/check-public.py .local/public-candidate
```

These have one clean root commit each and no remote. Proposed HTTPS URLs are
written into the candidate only; the grammar pin refers to the exported grammar
commit. The adapter uses the owner's approved Apache-2.0 LICENSE; the grammar retains
its Apache-2.0 license and upstream notices. The helper preserves these license
files, or accepts an explicitly approved replacement via `--adapter-license`.
Adapter licensing does not license the native server. See [publication
gates](PUBLISHING.md).

Public source checks need no compiler/runtime checkout or private GitHub access.
Private source, binary, CLI, internal evidence, captured archives and historical
validation Git objects are excluded from the exports. A pattern/allowlist audit
helps disclosure review; it does not make the inspectable native binary opaque.
macOS ARM64 dev-extension acceptance and performance recording are complete.
Public native asset promotion, native dependency review, recipient-machine
Gatekeeper acceptance and notarization remain separate deferred gates. No public
native asset is uploaded under the current private delivery choice. Linux, Windows,
physical Intel macOS and SSH/remote execution are pending.
