#!/usr/bin/env python3
"""Export reviewed source allowlists into fresh local Git histories. No upload."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--grammar', type=Path, default=root.parent/'tree-sitter-acore')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--adapter-url', default='https://github.com/AxiomCore/acore-zed')
parser.add_argument('--grammar-url', default='https://github.com/AxiomCore/tree-sitter-acore')
parser.add_argument('--release-pins', type=Path, help='Reviewed HTTPS pins; default stays disabled')
parser.add_argument('--adapter-license', type=Path, help='Owner-approved accepted license; draft remains private without this')
args = parser.parse_args()
for address in (args.adapter_url,args.grammar_url):
    parsed=urlparse(address)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        parser.error('Public source URLs must be plain HTTPS without credentials')
if args.output.exists(): parser.error('Use a new candidate directory; existing candidates are preserved')
allowlists=json.loads((root/'releases/public-files.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def git(directory,*argv):
    return subprocess.check_output(['git','-C',str(directory),*argv],text=True).strip()
def export(source,name):
    destination=args.output/name
    for relative in allowlists[name]:
        source_file=source/relative
        if source_file.is_symlink() or not source_file.is_file(): parser.error(f'Missing/symlink allowlisted file: {name}/{relative}')
        path=destination/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source_file,path)
        # A shared Cargo target directory can retain older include_str! inputs
        # when copy2 preserves timestamps. The exported source must rebuild.
        path.touch()
    return destination
adapter=export(root,'acore-zed'); grammar=export(args.grammar.resolve(),'tree-sitter-acore')
if args.release_pins:
    pins=json.loads(args.release_pins.read_text())
    for release in pins['releases']:
        for asset in release['assets']:
            url=urlparse(asset['url'])
            if url.scheme!='https' or not url.hostname or url.hostname in ('localhost','127.0.0.1') or url.username or url.password or url.query or url.fragment:
                parser.error('Public candidate must not contain development/credentialed asset URLs')
    shutil.copy2(args.release_pins,adapter/'releases/server.json')
    (adapter/'releases/server.json').touch()
if args.adapter_license:
    license_text=args.adapter_license.read_text()
    if not ('Permission is hereby granted, free of charge' in license_text or 'Apache License' in license_text):
        parser.error('Expected an owner-approved MIT or Apache-2.0 adapter license')
    (adapter/'LICENSE').write_text(license_text)
# A new root commit contains only allowlisted source; private history is absent.
for directory in (grammar,adapter):
    subprocess.run(['git','init','--quiet','--initial-branch=main',str(directory)],check=True)
    subprocess.run(['git','-C',str(directory),'add','--all'],check=True)
    subprocess.run(['git','-C',str(directory),'-c','user.name=AxiomCore contributors','-c','user.email=release-review@axiomcore.invalid','commit','--quiet','-m','Prepare reviewed source candidate'],check=True)
manifest=(adapter/'extension.toml').read_text().replace('repository = ""',f'repository = "{args.adapter_url}"',1)
manifest=manifest.replace('[grammars.acore]\nrepository = ""\nrev = ""',f'[grammars.acore]\nrepository = "{args.grammar_url}"\nrev = "{git(grammar,"rev-parse","HEAD")}"')
(adapter/'extension.toml').write_text(manifest)
subprocess.run(['git','-C',str(adapter),'add','extension.toml'],check=True)
subprocess.run(['git','-C',str(adapter),'-c','user.name=AxiomCore contributors','-c','user.email=release-review@axiomcore.invalid','commit','--quiet','--amend','--no-edit'],check=True)
license_text=(adapter/'LICENSE').read_text()
license_id='Apache-2.0' if 'Version 2.0, January 2004' in license_text else 'MIT' if 'Permission is hereby granted, free of charge' in license_text else 'private draft; owner accepted-license choice pending'
review={'publicPromotion':'pending; URLs are proposed, not verified published repositories','adapterLicense':license_id,'nativeTermsAndNotices':'separate owner approval pending','repositories':{}}
for directory in (grammar,adapter):
    files=git(directory,'ls-files').splitlines()
    assert git(directory,'rev-list','--count','HEAD')=='1'
    assert not git(directory,'status','--porcelain')
    assert not git(directory,'remote')
    review['repositories'][directory.name]={'path':str(directory.resolve()),'rootCommit':git(directory,'rev-parse','HEAD'),'historyCommits':1,'files':{p:sha(directory/p) for p in files}}
(args.output/'review.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({name:{'commit':repo['rootCommit'],'files':len(repo['files'])} for name,repo in review['repositories'].items()},indent=2))
