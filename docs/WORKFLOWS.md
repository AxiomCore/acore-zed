# Private inputs and explicit workflows for Zed (L7–L9)

The native LSP implements private JSON completion, hover, diagnostics, physical definition navigation and graph evidence for both VS Code and Zed. VS Code 0.2.5 provides task selection and its existing graph inspector. Zed 0.1.3 attaches the server to JSON as well as Acore/TOML and supplies copyable explicit tasks; its public extension API does not provide an equivalent graph panel. Use the CLI report in Zed.

Use a native server and CLI with the same `compilerVersion`. Use the public native 0.1.1 Mac ZIP from [INSTALL.md](INSTALL.md). The compatible CLI remains separately supplied and is not bundled or publicly released by this milestone. The adapter/grammar license does not license that compiler.

## Associate private inputs

Put `AxiomEditor.json` alongside the owning project's `AxiomDeps.toml`. Paths stay inside that project, including symlinks; another nested manifest owns a separate project. Flexible artifact names are supported. A recognized `format` identifies the role automatically; an explicit `role` is needed for untagged endpoint/credential files.

```json
{
  "format": "axiom-editor-inputs/v1",
  "artifacts": [
    {
      "path": "private/prepared-plan.json",
      "role": "server-plan",
      "inputs": {
        "contract": { "path": "api.axiom" },
        "schema": { "path": "storage.axiom" }
      }
    },
    {
      "path": "private/runtime-spec.json",
      "role": "runtime-spec",
      "resource": "tasks",
      "inputs": {
        "contract": { "path": "api.axiom" },
        "plan": { "path": "private/source-plan.json" },
        "schema": { "path": "storage.axiom" }
      }
    },
    { "path": "tests/application.json", "role": "application-suite" }
  ]
}
```

`sha256` is optional on each artifact and associated input; when supplied it must match captured bytes. A schema input can be a typed database package, a database contract JSON file, or a captured database `.acore` entry with its own manifest/dependencies. Use a typed package/contract when associating storage with a frontend/backend project.

Open a suite or authored binding and invoke completion on a property or enum value. Hover gives its wire documentation and semantic status. Unknown fields, invalid values, duplicates, missing inputs and stale digests are diagnosed. Navigate from a typed runtime table reference to its captured schema declaration. Signed/generated artifacts receive inspection and diagnostics; Acore does not offer editing completions or formatting for those artifacts. The host's independent JSON tooling remains available. Editing bytes never verifies a signature or grants runtime authority.

The 40 role schemas use the actual Rust wire types (plus the application runner report and editor association manifest). Schemas document canonical JSON object representations, rather than Serde's optional sequence encoding of structs. Cross-artifact semantic validation is additional and is reported explicitly: exact server plans/public contracts/current schemas, deployment/binding compatibility, D10 programs, application suites and database contract/inspection inputs have offline validators. Other roles report structural-only status. Live state, signature trust, provider permission and effective execution authority require their explicit CLI workflows. Planning policy is currently a pinned CLI policy identifier, not an invented editable JSON policy file. Binary `.axiomdb` bundles use explicit release/history inspection commands, not the JSON language server.

## Inspect impact

VS Code: run **Axiom: Show Graph** or **Axiom: Inspect Private Inputs**. Zed: run the explicit `editor/report` workflow or the command below.

```sh
"$ACORE_CLI" editor report --root "$PROJECT" --entry "$PROJECT/schema.acore" \
  --kind database --json > "$PROJECT/editor-report.json"
```

The report includes input roles/status, current diagnostics and graph evidence. PostgreSQL advanced/security/placement objects and SQLite objects retain their dialect. Managed steps, delivery/integration declarations, frontend forms/stores/persistence/policies/routes/guards/session/navigation have typed relationships. Prepared D10 mappings connect storage fields/tables to runtime operations, actions/endpoints and compatible frontend contracts using exact artifact digests and endpoint IDs. Missing/stale mappings are excluded. Opaque effects remain unknown. Facts are declared or compiler-derived; supplied origins remain distinct from current captured source, and runtime enforcement is not observed. Schema rename reports associated private consumers that require review before a new plan is prepared.

## Run a reviewed workflow

The catalogue is generated from the current CLI command tree. It covers 193 commands in the candidate, including server/dev/mock/delivery/package workflows; UI suites, compiler smoke, doctor/capabilities/host/package/extension workflows; and database offline/live inspection, planning/history/signing/execution/fleet/recovery/admission/runtime workflows. Showing the catalogue or validating an argument list never executes the selected command.

```sh
"$ACORE_LSP" --version-json
"$ACORE_CLI" editor info --json
"$ACORE_CLI" editor workflows --json
"$ACORE_CLI" editor validate-workflow --root "$PROJECT" \
  --request '{"workflow":"ui/test","inputs":{"source":"main.acore","suite":"tests/application.json","target":"web","layer":"reference","report":"application-report.json"}}'
```

Workflow IDs use `/` between CLI words. Input IDs/types/options come from the catalogue, including required inputs, repeated flags, choices and defaults. Unknown options, malformed types, escaping paths and paths inside a different nested Axiom project are rejected. The actual CLI parser checks requirements/conflicts. No shell or arbitrary `extraArgs` field is supported. Inputs with spaces/punctuation are literal arguments. CLI domain validators still decide target/provider/runtime support when the explicit command executes.

VS Code: save the owning project's inputs, set `axiom.binaryPath` to the compatible CLI, then run **Axiom: Run CLI Workflow**. Select a workflow and its typed inputs. **Axiom: Test Project** requires a suite. The separate `smoke` task is labeled **Compiler smoke (zero application assertions)**. A selected application suite must report nonzero real assertions to pass. Tasks recheck trust, native/CLI identity, saved inputs and project revision before execution. Cancel through VS Code's task controls; the owned process group and descendants are cleaned up.

You can persist a reviewed definition in `axiom.workflows` or `.vscode/tasks.json`:

```json
{
  "type": "axiom-workflow",
  "project": "file:///absolute/owning-project",
  "workflow": "ui/test",
  "inputs": {
    "source": "main.acore",
    "suite": "tests/application.json",
    "target": "web",
    "layer": "reference",
    "report": "application-report.json"
  }
}
```

For Zed, copy `scripts/run-workflow.py` from this adapter into the owning project's `.zed/` directory, copy `templates/workflow-tasks.json` to `.zed/tasks.json`, and save the same typed definition as `.zed/acore-workflow.json`. Set the template's `ACORE_CLI`, `ACORE_LSP` and `ACORE_PYTHON` to your compatible executables (Python 3.9+). `ACORE_LSP` must be the server selected in Zed. Set `project` to the canonical owning directory's file URI. Open that directory as the worktree, or adjust `ACORE_PROJECT_ROOT` and the definition path to the actual owning project.

Invoke **task: spawn** and select **Acore: run reviewed CLI workflow (save all)**. The task explicitly saves all buffers, acknowledges the reviewed worktree, validates the compiler/arguments and fences saved files before dispatch. It has no save hooks. Cancel using Zed's task terminal controls. Signing, provider connections, setup and mutations are available only through an explicitly selected workflow. Review those inputs before invoking it. The runner bounds metadata time/output and removes its own descendants on cancellation or parent exit. [Zed task configuration](https://zed.dev/docs/tasks).

## Local verification

```sh
"$ACORE_CLI" editor check --root "$PROJECT" --entry "$PROJECT/main.acore" \
  --kind frontend --target web --json
"$ACORE_CLI" ui test "$PROJECT/main.acore" --target web \
  --lock "$PROJECT/axiom.ui.lock.json" --suite "$PROJECT/tests/application.json" \
  --layer reference --report "$PROJECT/application-report.json"
```

Use `editor check --help` and the generated workflow catalogue for the exact singular/plural option spelling in your CLI. The candidate exposes `editor/report`'s repeated `targets` input as `--target`.

Apple Silicon macOS is the acceptance platform for this milestone. Intel macOS, Linux and Windows acceptance, hosted Actions and registry promotion remain pending after the L10 Mac delivery.
