#!/usr/bin/env python3
"""Exercise the copyable POSIX task templates' shell/path boundary.

This checks literal argv, cwd and opt-in policy using a recording executable,
not compiler semantics or Zed UI acceptance. No third-party dependencies.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    if os.name != "posix":
        raise SystemExit("POSIX template check requires /bin/sh; Windows acceptance is pending")
    tasks = []
    for name in ("check-tasks.json", "foreign-tasks.json", "tooling-tasks.json"):
        tasks.extend(json.loads((ROOT / "templates" / name).read_text()))
    with tempfile.TemporaryDirectory(prefix="acore-zed-tasks-") as temporary:
        # If a path ever becomes shell code, it can create this marker only
        # inside this disposable directory. The correct templates never do.
        parent = Path(temporary)
        owner = parent / "Project $cash; 'quote' $(touch TASK_INJECTION)"
        owner.mkdir()
        cli = parent / "axiom $tool; 'literal'"
        cli.write_text(
            f"#!{sys.executable}\n"
            "import json, os, sys\n"
            "print(json.dumps({'argv':sys.argv[1:], 'cwd':os.getcwd()}))\n"
        )
        cli.chmod(0o700)
        for task in tasks:
            assert task["save"] == "none", task["label"]
            assert not task.get("hooks") and not task.get("tags"), task["label"]
            assert task["allow_concurrent_runs"] is False
            assert task["reveal"] == "always" and task["hide"] == "never"
            assert task["shell"] == {"program": "/bin/sh"}
            assert task["command"] == '"$ACORE_CLI"'
            assert "$ZED_" not in task["command"] + " ".join(task["args"])
            env = os.environ.copy()
            resolved = {
                key: value.replace("$ZED_WORKTREE_ROOT", str(owner))
                for key, value in task["env"].items()
            }
            resolved["ACORE_CLI"] = str(cli)
            env.update(resolved)
            cwd = task["cwd"].replace("$ZED_WORKTREE_ROOT", str(owner))
            command = " ".join([task["command"], *task["args"]])
            result = subprocess.run(
                ["/bin/sh", "-i", "-c", command], cwd=cwd, env=env,
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, (task["label"], result.stderr)
            report = json.loads(result.stdout)
            expected = [
                resolved[arg[2:-1]] if arg.startswith('"$ACORE_') else arg
                for arg in task["args"]
            ]
            assert report["argv"] == expected, (task["label"], report)
            assert Path(report["cwd"]).resolve() == owner.resolve()
            assert not (owner / "TASK_INJECTION").exists()
            assert not (parent / "TASK_INJECTION").exists()
        print(f"{len(tasks)} task templates pass literal path/argv and explicit-run checks")


if __name__ == "__main__":
    main()
