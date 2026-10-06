# Run explicit CLI tasks in Zed

Core editing needs only `acore-lsp`. The separate `axiom` CLI is optional;
its executable is independent of `lsp.acore-lsp.binary.path`. Install a
compatible CLI through your team's existing distribution route. The public
Mac ARM64 server ZIP and its verification steps are documented in
[INSTALL.md](INSTALL.md).

Confirm the tools from the same environment as Zed's worktree terminal:

```sh
command -v axiom
axiom --version
axiom editor --help
axiom editor info --json
acore-lsp --version-json
```

The tested CLI reports `axiom-editor-cli/v1`, `axiom-editor/v1` and check format
`axiom-editor-check/v1`. It supports `editor check`, `editor refresh-extraction`
and `extensions prepare-ide`. There is no `editor prepare-native` command in
this candidate. Use the actual CLI help when choosing additional operations.
For saved-check parity and extraction-cache reuse, compare `compilerVersion`
from `axiom editor info --json` with `acore-lsp --version-json`. The accepted
pair uses the same fingerprint. A protocol-compatible older CLI can still run
its own saved checks, but its extraction cache is rejected by a different
compiler build; upgrade the CLI and refresh explicitly. SDK receipts have
their separate source/interface/helper digest checks.

## Install a project-local task

Copy the appropriate objects from [check-tasks.json](../templates/check-tasks.json),
[tooling-tasks.json](../templates/tooling-tasks.json) or
[foreign-tasks.json](../templates/foreign-tasks.json) into the owning worktree's
`.zed/tasks.json` array. These are copyable templates, not extension-installed
or global tasks. Set `env.ACORE_CLI` to `axiom` for worktree PATH discovery or to
the absolute CLI executable. Keep the quoted `command` and path arguments.

With an Acore file active, invoke **task: spawn** and choose the task. In the
accepted macOS setup the shortcut is **Cmd-Shift-R**. The terminal stays visible,
prints the CLI output and displays success or the nonzero exit code. Check tasks
produce JSON in the terminal; this adapter does not import CLI output into Zed's
Problems panel. Missing tools produce a terminal error; install the CLI or fix
`ACORE_CLI`. CLI failure does not disable the separately selected language server.

Every template uses `save: "none"`: it checks or prepares the files already on
disk without saving editor buffers. Use **workspace: save all** first when you
intend to check current edits. Review all buffers before that action. An unsaved
invalid buffer can have LSP errors while the saved CLI check succeeds. Saving it
makes the next CLI check fail too. To deliberately save before a task, change
that task to `save: "all"`; Zed saves all edited buffers, including other owners,
not just the task's project. `save: "current"` does not save imported inputs.

Tasks have no `hooks` or runnable tags. Opening, editing, saving, completion and
hover do not launch them. **task: rerun** reuses its previously resolved context;
use **task: spawn** after changing tasks, worktrees, entries or target selections.
Use Zed's terminal/task controls to stop an explicitly launched command. Cancelling
preparation/extraction can leave partial outputs; review them and rerun explicitly.

## Select the owning project

The default templates assume the worktree itself owns the selected project.
Configuration/backend/frontend default to `main.acore`; database defaults to
`schema.acore`. A file in a multi-project outer worktree needs a pinned nested
owner and entry. For a backend in `backend/`, change these fields:

```json
{
  "cwd": "$ZED_WORKTREE_ROOT/backend",
  "env": {
    "ACORE_CLI": "axiom",
    "ACORE_PROJECT_ROOT": "$ZED_WORKTREE_ROOT/backend",
    "ACORE_ENTRY": "$ZED_WORKTREE_ROOT/backend/main.acore"
  }
}
```

Keep `--kind backend` in its arguments. The CLI rejects an outer root that does
not own the entry; tasks do not infer owners from the current cursor. Use one
reviewed task per owner. Set `ACORE_ENTRY` to the actual entry and optionally add
supported literal `--target web` / `--variant default` arguments after checking
`axiom editor check --help`. Database tasks remain offline; no database connection
or migration task is inferred.

Zed tasks are shell commands, even with an argument array. The accepted templates
use `/bin/sh`, put paths in environment values, and expand them as quoted
`"$ACORE_PROJECT_ROOT"`, `"$ACORE_ENTRY"` and `"$ACORE_CLI"`. Zed substitutes
`$ZED_WORKTREE_ROOT` in those environment values; the shell then treats their
contents as data. Actual Zed acceptance covers spaces, dollar signs, semicolons
and single quotes in an owner path and spaces in the executable path. Do not
splice raw `$ZED_FILE`, selected text or root paths into the shell command.
`cwd` is a path field and is not shell-quoted. These POSIX-shell templates have
macOS ARM64 acceptance; Linux, Windows and Intel macOS acceptance remain pending.
[Zed task configuration](https://zed.dev/docs/tasks),
[pinned task environment handling](https://github.com/zed-industries/zed/blob/76659a55a8c10ed355a070f8764a0b1733e3c115/crates/task/src/task_template.rs).

## Confirm the saved check directly

Run from the same owning project with reviewed paths:

```sh
axiom editor check --root "/path/to/config" --entry "/path/to/config/main.acore" --kind config --json
axiom editor check --root "/path/to/backend" --entry "/path/to/backend/main.acore" --kind backend --json
axiom editor check --root "/path/to/frontend" --entry "/path/to/frontend/main.acore" --kind frontend --json
axiom editor check --root "/path/to/database" --entry "/path/to/database/schema.acore" --kind database --json
```

Check `format: axiom-editor-check/v1`, `saved: true`, owner kind/entry URI,
`valid` and diagnostic spans. Warnings can accompany a successful check. Invalid
inputs exit nonzero. The four saved checks are static and write no build/cache
artifacts. Build/run/test/resolve/migration are separate existing CLI workflows;
they are not added as automatic actions by this extension.

See [foreign workflows](FOREIGN_WORKFLOWS.md) for explicit SDK preparation and
native extraction, physical language tooling, stale inputs and recovery.
