#!/usr/bin/env python3
"""Prepare an installable local extension without publishing private paths."""
import argparse
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--grammar', type=Path, default=root.parent / 'tree-sitter-acore')
parser.add_argument('--output', type=Path, default=root / '.local/dev-extension')
parser.add_argument('--release-pins', type=Path, help='Embed a reviewed private release pin file for installer acceptance')
args = parser.parse_args()
grammar = args.grammar.resolve()
revision = subprocess.check_output(['git', '-C', str(grammar), 'rev-parse', 'HEAD'], text=True).strip()
dirty = subprocess.check_output(['git', '-C', str(grammar), 'status', '--porcelain'], text=True).strip()
if dirty:
    parser.error('Commit the tested grammar revision locally before generating a pinned development manifest.')
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
for name in ['src', 'languages', 'snippets', 'releases']:
    shutil.copytree(root / name, output / name, dirs_exist_ok=True)
if args.release_pins:
    shutil.copy2(args.release_pins, output / 'releases/server.json')
# copy2 preserves old mtimes; force Cargo's include_str! dependency to notice
# a changed release pin set, including rollback to an older candidate.
(output / 'releases/server.json').touch()
for name in ['Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'LICENSE',
             'LICENSE-THIRD-PARTY-APACHE-2.0', 'THIRD_PARTY_NOTICES.md']:
    shutil.copy2(root / name, output / name)
manifest = (root / 'extension.toml').read_text()
manifest = manifest.replace('[grammars.acore]\nrepository = ""\nrev = ""',
    f'[grammars.acore]\nrepository = "{grammar.as_uri()}"\nrev = "{revision}"')
(output / 'extension.toml').write_text(manifest)
print(output)
