# Native server release status

Updated: 7 October 2026.

Acore LSP **0.1.2** is the corrected macOS ARM64 server. Zed adapter **0.1.4**
pins that exact executable and refuses withdrawn versions. The compatible CLI is
**0.148.1**. See [installation and verification](INSTALL.md).

Native LSP **0.1.0 and 0.1.1** downloads are withdrawn because their executable
contained implementation text that was not intended for distribution. Do not
install or redistribute these builds, or use them as rollback candidates.
Already downloaded copies and external caches cannot be recalled. This finding
has not established a production credential compromise or malicious behavior.

Only macOS ARM64 has release acceptance. Intel macOS, Linux, Windows, remote
hosts and registry installation remain pending. These packages have ad-hoc
macOS signatures; Developer ID notarization and recipient-machine Gatekeeper
acceptance are not certified. Use an approved signed build if your system blocks
execution; these instructions do not bypass operating-system protections.

The Apache-2.0 adapter/grammar and the proprietary native compiler have separate
terms. Keep the native release's NATIVE-NOTICE.txt and third-party notices with
the executable. Client executable bytes are inspectable.

If an upgrade fails, temporarily disable the Acore language server or use only a
previously verified source-clean build. Do not fall back to 0.1.0 or 0.1.1. A
missing asset, unsupported platform, wrong checksum or incompatible cached file
must produce an error rather than selecting an unverified server.
