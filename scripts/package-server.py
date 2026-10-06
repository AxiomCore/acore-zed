#!/usr/bin/env python3
"""Prepare immutable macOS ARM64 server assets for review; never upload them."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
from urllib.parse import urlparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--binary', type=Path, required=True)
parser.add_argument('--expected-sha256', required=True, help='Digest from the trusted native build receipt')
parser.add_argument('--release-id', required=True)
parser.add_argument('--asset-base-url', required=True, help='Immutable release directory; no API/latest endpoint')
parser.add_argument('--development-url', action='store_true', help='Allow only loopback HTTP in a private test candidate')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
binary = args.binary.resolve()
data = binary.read_bytes()
digest = hashlib.sha256(data).hexdigest()
if not re.fullmatch('[0-9a-f]{64}', args.expected_sha256) or digest != args.expected_sha256:
    parser.error('Binary does not match the trusted SHA-256; it was not executed')
if not re.fullmatch('[A-Za-z0-9_-]{1,100}', args.release_id):
    parser.error('Release ID must be an immutable safe path token')
# This phase accepts only the physical Apple Silicon host; other assets stay absent.
if data[:8] != struct.pack('<II', 0xfeedfacf, 0x0100000c):
    parser.error('Only a thin macOS ARM64 Mach-O server is accepted by this packaging gate')
base = args.asset_base_url.rstrip('/')
url = urlparse(base)
development = args.development_url and url.scheme == 'http' and url.hostname == '127.0.0.1' and url.port
if (url.scheme != 'https' and not development) or not url.hostname or url.username or url.password or url.query or url.fragment:
    parser.error('Use an HTTPS immutable release directory, or explicit loopback development URL')
if not url.path or args.release_id not in url.path.split('/') or any(x in url.path.split('/') for x in ('latest','..')):
    parser.error('The release directory must contain the exact release ID; latest and traversal are rejected')
if args.output.exists():
    parser.error('Use a new output directory; existing release candidates are never overwritten')
info = json.loads(subprocess.check_output([str(binary),'--version-json'], text=True))
if not str(info.get('serverVersion','')).startswith('acore/') or info.get('protocolVersion') != 'axiom-editor/v1' or not re.fullmatch('[0-9a-f]{64}',info.get('compilerVersion','')) or info.get('editorFeatures',{}).get('virtualDocumentNavigationOptOut') is not True:
    parser.error('Server metadata is not compatible with this Zed adapter')
asset = f'acore-lsp-macos-aarch64-{digest}.bin'
pins = {'format':'acore-server-releases/v1','activeRelease':args.release_id,'releases':[{
    'id':args.release_id,'serverVersion':info['serverVersion'],'protocolVersion':info['protocolVersion'],
    'compilerVersion':info['compilerVersion'],'virtualDocumentNavigationOptOut':True,
    'assets':[{'platform':'macos-aarch64','url':base+'/'+asset,'sha256':digest,'size':len(data)}]
}]}
args.output.mkdir(parents=True)
shutil.copy2(binary,args.output/asset)
(args.output/'server.json').write_text(json.dumps(pins,indent=2)+'\n')
(args.output/'SHA256SUMS').write_text(f'{digest}  {asset}\n')
(args.output/'DISTRIBUTION-REVIEW.md').write_text('''# Native server distribution candidate

This is a private review artifact. It has not been approved for public redistribution.
Only the macOS ARM64 raw executable is present; the extension must download it
separately. No CLI, compiler/runtime source archive or native executable is bundled
in the adapter. The raw executable avoids archive extraction and path traversal.

Before public promotion, approve native redistribution terms and third-party
notices, inspect executable disclosure, and decide signing/notarization policy.
Any signing or stripping changes bytes: package the final binary again and pin
its new SHA-256/size. Never replace an existing release asset with new bytes.
No supported Intel, Linux or Windows asset is implied by this package.
''')
print(json.dumps({'output':str(args.output.resolve()),'asset':asset,'sha256':digest,'size':len(data),'metadata':info,'publicPromotion':'pending owner/license/notices/signing review','developmentUrl':bool(development)},indent=2))
