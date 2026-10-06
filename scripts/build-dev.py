#!/usr/bin/env python3
"""Build the locked WASI component and update an existing Zed dev installation."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tempfile
import uuid

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--grammar', type=Path, default=root.parent / 'tree-sitter-acore')
parser.add_argument('--output', type=Path, default=root / '.local/dev-extension')
parser.add_argument('--release-pins', type=Path, help='Reviewed private installer candidate; source defaults remain unchanged')
parser.add_argument('--wasi-sdk', type=Path, help='WASI SDK root; defaults to WASI_SDK_PATH or Zed\'s existing Mac cache')
parser.add_argument('--installed-dev-link', type=Path,
                    help='Refresh only an existing Zed dev symlink pointing at the output')
args = parser.parse_args()
output = args.output.resolve()
sdk = args.wasi_sdk or (Path(os.environ['WASI_SDK_PATH']) if os.environ.get('WASI_SDK_PATH') else
                       Path.home() / 'Library/Application Support/Zed/extensions/build/wasi-sdk')
clang = sdk / 'bin' / ('clang.exe' if os.name == 'nt' else 'clang')
if args.installed_dev_link:
    installed = args.installed_dev_link.absolute()
    if not installed.is_symlink() or installed.resolve() != output:
        raise RuntimeError('Installed dev link must be a symlink to the generated output')
    if not clang.is_file():
        raise RuntimeError('Refreshing an installed extension requires --wasi-sdk so its grammar is rebuilt too; use Zed\'s dev installation action otherwise')
configure = [sys.executable, str(root / 'scripts/configure-dev.py'),
             '--grammar', str(args.grammar), '--output', str(output)]
if args.release_pins:
    configure.extend(['--release-pins', str(args.release_pins.resolve())])
subprocess.run(configure, check=True)
# Compile the generated copy so include_str! embeds its actual release pins.
target = Path(os.environ.get('CARGO_TARGET_DIR', str(root / 'target'))).resolve()
subprocess.run(['cargo', '+1.93.0', 'build', '--locked', '--release', '--target', 'wasm32-wasip2'],
               cwd=output, env=dict(os.environ, CARGO_TARGET_DIR=str(target)), check=True)
component = (target / 'wasm32-wasip2/release/acore_zed.wasm').read_bytes()
if component[:8] != b'\x00asm\x0d\x00\x01\x00':
    raise RuntimeError('Rust output must be a WASI component, not a core module')
# Rust's WASI preview2 output already is a component. Zed's builder strips
# debug custom sections; the release component also loads with them retained.
with tempfile.NamedTemporaryFile(dir=output, prefix='.component-', delete=False) as temporary:
    temporary.write(component)
    candidate = Path(temporary.name)
os.replace(candidate, output / 'extension.wasm')
# Match Zed's grammar build, including the external scanner. A Rust component
# alone cannot load the language. See the upstream extension_builder.rs:
# https://github.com/zed-industries/zed/blob/main/crates/extension/src/extension_builder.rs
if clang.is_file():
    grammar_output = output / 'grammars'
    grammar_output.mkdir(exist_ok=True)
    grammar_source = args.grammar.resolve() / 'src'
    candidate = grammar_output / ('.acore-' + uuid.uuid4().hex + '.wasm')
    command = [str(clang), '-fPIC', '-shared', '-Os', '-Wl,--export=tree_sitter_acore',
               '-o', str(candidate), '-I', str(grammar_source), str(grammar_source / 'parser.c')]
    if (grammar_source / 'scanner.c').is_file():
        command.append(str(grammar_source / 'scanner.c'))
    subprocess.run(command, check=True)
    if candidate.read_bytes()[:8] != b'\x00asm\x01\x00\x00\x00':
        raise RuntimeError('Tree-sitter output must be a core WebAssembly module')
    os.replace(candidate, grammar_output / 'acore.wasm')
# Zed watches installed extension files. A manifest change requests reindex/
# reload after the complete component is in place; trust/settings are untouched.
(output / 'extension.toml').touch()
if args.installed_dev_link:
    # The installed-directory watcher does not follow out-of-tree symlink
    # changes. Replace the identical link atomically to notify that watcher.
    replacement = installed.with_name('.acore-reload-' + uuid.uuid4().hex)
    replacement.symlink_to(os.readlink(installed), target_is_directory=True)
    os.replace(replacement, installed)
print(f'Built dev component: {output / "extension.wasm"}')
if not clang.is_file():
    print('No existing WASI SDK: Zed must compile the grammar during first dev installation.')
print('For first installation, use zed: install dev extension with this directory.')
