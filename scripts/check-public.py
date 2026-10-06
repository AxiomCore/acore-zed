#!/usr/bin/env python3
"""Verify an exported source candidate and its complete one-commit Git history."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('candidate',type=Path)
args=parser.parse_args()
review=json.loads((args.candidate/'review.json').read_text())
allowlists=json.loads((args.candidate/'acore-zed/releases/public-files.json').read_text())
problems=[]; blobs=0
for name,record in review['repositories'].items():
    root=args.candidate/name
    def git(*argv):return subprocess.check_output(['git','-C',str(root),*argv])
    tracked=git('ls-files').decode().splitlines()
    assert set(tracked)==set(allowlists[name]),f'{name}: changed allowlist'
    assert git('rev-list','--count','--all').strip()==b'1',f'{name}: private history included'
    assert git('status','--porcelain').strip()==b'',f'{name}: dirty candidate'
    assert git('remote').strip()==b'',f'{name}: unexpected remote'
    for filename,digest in record['files'].items():
        path=root/filename
        assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,filename
    # Inspect every reachable blob, including history, not only the working tree.
    for row in git('rev-list','--objects','--all').decode().splitlines():
        object_id=row.split(' ',1)[0]
        if git('cat-file','-t',object_id).strip()!=b'blob':continue
        data=git('cat-file','blob',object_id);blobs+=1
        if data.startswith((b'\x00asm',b'\xcf\xfa\xed\xfe',b'\x7fELF',b'MZ',b'\x1f\x8b')):
            problems.append(f'{name}: binary/archive blob {row}')
        private_paths = b'|'.join([b'/' + b'Users/[^/\\s]+/', b'/' + b'Volumes/', b'/' + b'private/tmp/', b'/' + b'tmp/axiom-'])
        secrets = rb'BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16}'
        if re.search(private_paths + b'|' + secrets,data):
            problems.append(f'{name}: private path/credential pattern in {row}')
    lock=(root/'Cargo.lock')
    if lock.exists():
        # Native sources must not be needed to build the public adapter.
        text=(root/'Cargo.toml').read_text()
        assert 'path =' not in text and 'git =' not in text,'native/private Cargo dependency'
assert not problems,problems
print(json.dumps({'result':'pass','repositories':len(review['repositories']),'historyCommitsPerRepository':1,'reachableBlobsInspected':blobs,'allowlistFileHashesVerified':sum(len(r['files']) for r in review['repositories'].values()),'publicPromotion':review['publicPromotion'],'limits':'Pattern/allowlist/history audit, not a proof that native binaries conceal implementation'},indent=2))
