# Measured macOS performance and support

Release acceptance uses Apple M2, macOS 26.2 ARM64 and Zed 1.22.0. The final
native candidate uses editor protocol `axiom-editor/v1` with the required
virtual-navigation opt-out. Linux x64, Windows x64, remote execution and
physical Intel macOS acceptance remain pending. Only macOS ARM64 has accepted
native artifacts; syntax/WASI portability is not platform certification.

The native benchmark uses Zed's `workspaceTrusted: false` and
`virtualDocumentNavigation: false` settings. Each file has a typed declaration
and a real import edge; most bytes are comment padding. These synthetic
configuration corpora are useful for comparison, not a claim about every
backend, frontend, database or foreign dependency workload.

| Measurement | 100 files / 5,193,749 bytes | 1,000 files / 26,222,662 bytes |
| --- | ---: | ---: |
| Cold process-to-captured-project readiness | 829 ms | 2,695 ms |
| Warm completion p95, 30 samples | 9.8 ms | 61.2 ms |
| Warm hover p95, 30 samples | 8.3 ms | 51.4 ms |
| Warm physical definition p95, 30 samples | 12.0 ms | 44.6 ms |
| Current diagnostic refresh p95, 10 edits | 813 ms | 3,384 ms |
| Native process RSS after repeated edits | 84.3 MiB | 408.2 MiB |
| Captured source/configuration inputs | 119 | 1,019 |

Warm request-to-response targets are 100 ms for completion and 75 ms for
hover/definition. Readiness targets are 2 seconds on the smaller corpus and
8 seconds on the larger one; memory targets are 256/512 MiB respectively.
These targets pass for this measurement. The proposed smaller-corpus current
diagnostic budget is 500 ms, including debounce: **it does not pass**. Large
project diagnostics can take several seconds after an edit. The earlier E7
diagnostic miss remains a known limit; no improvement is claimed from changing
clients. The benchmark includes native work and Python framing/polling overhead,
not Zed render time, installer transfer, grammar build or editor activation.

macOS can compress/page process memory, so RSS is a point-in-time measurement,
not peak allocation or total editor memory. Background builds and host load
affect timing. Real-Zed acceptance separately checks useful typed responses,
visible feedback, keyboard workflows, unsaved recovery and process cleanup.
Theme-dependent colors have visual acceptance on the tested dark theme;
screen-reader and forced-colors acceptance is not claimed.

Future platform acceptance must supply a native artifact with a trusted digest,
run the [smoke check](TESTING.md), and perform the manual suite in the actual
Zed desktop client on that execution host. Retain failures and budget misses.
The public source workflow can build the portable adapter on a runner; native
compiler builds stay in the private pipeline. Actions billing recovery does not
prevent local macOS tests, and no other OS becomes supported from CI alone.
