#!/usr/bin/env python3
"""Explicit Zed tasks use the same typed CLI validator as VS Code.

No save hooks. The supplied task saves all buffers before this runner starts.
All CLI launches use literal argv, owning cwd and an owned process group.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import time

LIMIT = 8 * 1024 * 1024
owned = None

def stop(signum=None, frame=None):
    if owned is not None and owned.poll() is None:
        try:os.killpg(owned.pid, signal.SIGTERM)
        except ProcessLookupError:pass
        try: owned.wait(timeout=1.5)
        except subprocess.TimeoutExpired: os.killpg(owned.pid, signal.SIGKILL); owned.wait()
    if signum is not None: raise KeyboardInterrupt

def run(argv, root, metadata=False):
    global owned
    owned=subprocess.Popen(argv,cwd=root,shell=False,start_new_session=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    sel=selectors.DefaultSelector();sel.register(owned.stdout,selectors.EVENT_READ,True);sel.register(owned.stderr,selectors.EVENT_READ,False)
    output=bytearray();errors=bytearray();total=0;deadline=time.monotonic()+15 if metadata else None
    try:
        while sel.get_map():
            if deadline is not None and time.monotonic()>deadline: raise ValueError('CLI metadata request timed out')
            for key,_ in sel.select(timeout=.1):
                data=os.read(key.fileobj.fileno(),65536)
                if not data:sel.unregister(key.fileobj);continue
                total+=len(data)
                if total>LIMIT: raise ValueError('CLI workflow output exceeds 8 MiB')
                (output if key.data else errors).extend(data)
                if not metadata: (sys.stdout.buffer if key.data else sys.stderr.buffer).write(data);sys.stdout.flush();sys.stderr.flush()
        code=owned.wait()
        if metadata and code:raise ValueError(errors.decode(errors='replace')[:8192] or f'CLI metadata failed ({code})')
        return code,output.decode(errors='replace')
    finally:
        # Clean descendants even if the entry process already exited.
        try:os.killpg(owned.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        owned.wait();owned=None;sel.close()

def revision(root, selected_paths=()):
    """Fence saved project inputs without following links or nested projects."""
    digest=hashlib.sha256();size=0;inputs=set()
    ignored={'.git','target','node_modules','dist','build','vendor','.venv'}
    for directory,dirs,files in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in ignored and not (Path(directory)/d).is_symlink() and not ((Path(directory)/d/'AxiomDeps.toml').exists()))
        for name in sorted(files):
            p=Path(directory)/name
            if p.is_symlink() or p.suffix not in {'.acore','.json','.jsonc','.toml','.axiom','.axiomdb','.lock','.py','.yaml','.yml'}:continue
            inputs.add(p)
            if len(inputs)>2048:raise ValueError('Saved workflow input fence exceeds 2048 inputs; select the owning project')
    for value in selected_paths:
        p=(root/value).resolve()
        if not p.is_relative_to(root):raise ValueError('Workflow path escapes its owning project')
        if p.is_file():inputs.add(p)
    if len(inputs)>2048:raise ValueError('Saved workflow input fence exceeds 2048 inputs; select the owning project')
    for p in sorted(inputs):
        size+=p.stat().st_size
        if size>32*1024*1024:raise ValueError('Saved workflow input fence exceeds 32 MiB; select the owning project')
        digest.update(str(p.relative_to(root)).encode());digest.update(hashlib.sha256(p.read_bytes()).digest())
    return digest.hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path);parser.add_argument('--cli',required=True);parser.add_argument('--definition',required=True,type=Path)
    parser.add_argument('--trusted-workspace',action='store_true',help='Explicitly acknowledge the reviewed owning worktree before running a task')
    args=parser.parse_args()
    if not args.trusted_workspace:raise ValueError('Explicit workflow requires a trusted, reviewed owning worktree')
    root=args.root.resolve(strict=True);path=args.definition.resolve(strict=True)
    if not root.is_dir() or not path.is_relative_to(root) or path.stat().st_size>65536:raise ValueError('Workflow definition must be a bounded owning-project file')
    definition=json.loads(path.read_text())
    if set(definition)!={'type','project','workflow','inputs'} or definition['type']!='axiom-workflow' or definition['project'].rstrip('/')!=root.as_uri().rstrip('/') or not isinstance(definition['inputs'],dict):raise ValueError('Use the exact typed workflow shape and owning-project file URI')
    if definition['workflow']=='ui/test' and not definition['inputs'].get('suite'):raise ValueError('Application-test workflow requires suite; compiler smoke is a separate task')
    before=revision(root)
    _,raw=run([args.cli,'editor','workflows','--json'],root,True);catalog=json.loads(raw)
    if catalog.get('format')!='axiom-editor-workflows/v1':raise ValueError('CLI does not support typed editor workflows')
    server=os.environ.get('ACORE_LSP')
    if not server:raise ValueError('Set ACORE_LSP to the native server selected in Zed; a matching compiler is required')
    _,raw=run([server,'--version-json'],root,True)
    if json.loads(raw).get('compilerVersion')!=catalog.get('compilerVersion'):raise ValueError('CLI/native compiler mismatch')
    workflow=next((w for w in catalog['workflows'] if w['id']==definition['workflow']),None)
    if workflow is None:raise ValueError('Unsupported CLI workflow')
    paths=[]
    for field in workflow['inputs']:
        if field['valueType']=='path':
            value=definition['inputs'].get(field['id'])
            paths.extend([value] if isinstance(value,str) else [p for p in value if isinstance(p,str)] if isinstance(value,list) else [])
    if revision(root)!=before:raise ValueError('Saved inputs changed during workflow preparation; retry')
    before=revision(root,paths)
    request=json.dumps({'workflow':definition['workflow'],'inputs':definition['inputs']},separators=(',',':'))
    _,raw=run([args.cli,'editor','validate-workflow','--root',str(root),'--request',request],root,True);validation=json.loads(raw)
    if validation.get('format')!='axiom-editor-workflow-validation/v1' or validation.get('compilerVersion')!=catalog['compilerVersion'] or not isinstance(validation.get('argv'),list) or not all(isinstance(a,str) for a in validation['argv']):raise ValueError('Invalid CLI workflow response')
    if revision(root,paths)!=before:raise ValueError('Saved inputs changed during workflow preparation; retry')
    print(validation['label']);print('Literal argv:',json.dumps(validation['argv']),flush=True)
    code,output=run([args.cli,*validation['argv']],root)
    if not code and validation['reportKind']=='application-assertions':
        counts=re.search(r'(\d+) assertions',output)
        if not counts or int(counts[1])==0:raise ValueError('No application assertions were reported; acceptance did not pass')
    print(f'CLI workflow {"completed" if code==0 else "failed"} (exit {code}).',flush=True)
    return code

if __name__=='__main__':
    signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
    try:sys.exit(main())
    except KeyboardInterrupt:stop();print('Workflow cancelled.',file=sys.stderr);sys.exit(130)
    except (ValueError,OSError,KeyError,TypeError) as error:stop();print(f'Workflow failed: {error}',file=sys.stderr);sys.exit(1)
