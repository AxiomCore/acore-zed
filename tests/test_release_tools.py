"""Subprocess checks at the native execution and public export boundaries."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class ReleaseTools(unittest.TestCase):
    def package(self,binary,digest,output):
        return subprocess.run([sys.executable,str(ROOT/'scripts/package-server.py'),
            '--binary',str(binary),'--expected-sha256',digest,'--release-id','test-release',
            '--asset-base-url','https://example.org/releases/test-release','--output',str(output)],
            capture_output=True,text=True)

    def test_bad_trusted_digest_does_not_execute_the_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);marker=directory/'executed';binary=directory/'candidate'
            binary.write_text('#!/bin/sh\ntouch "'+str(marker)+'"\n');binary.chmod(0o755)
            result=self.package(binary,'0'*64,directory/'out')
            self.assertNotEqual(result.returncode,0);self.assertIn('trusted SHA-256',result.stderr)
            self.assertFalse(marker.exists());self.assertFalse((directory/'out').exists())

    def test_wrong_native_format_is_not_executed_even_with_matching_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);marker=directory/'executed';binary=directory/'candidate'
            binary.write_text('#!/bin/sh\ntouch "'+str(marker)+'"\n');binary.chmod(0o755)
            result=self.package(binary,hashlib.sha256(binary.read_bytes()).hexdigest(),directory/'out')
            self.assertNotEqual(result.returncode,0);self.assertIn('macOS ARM64',result.stderr)
            self.assertFalse(marker.exists())

    def test_public_export_has_clean_history_and_excludes_ignored_canary(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'candidate'
            canary=ROOT/'.local/z6/disclosure-canary';canary.parent.mkdir(parents=True,exist_ok=True)
            canary.write_text('private compiler capture sentinel\n')
            try:
                result=subprocess.run([sys.executable,str(ROOT/'scripts/prepare-public.py'),'--output',str(output)],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertFalse((output/'acore-zed/.local').exists())
                check=subprocess.run([sys.executable,str(ROOT/'scripts/check-public.py'),str(output)],capture_output=True,text=True)
                self.assertEqual(check.returncode,0,check.stderr)
                for repo in ('acore-zed','tree-sitter-acore'):
                    self.assertEqual(subprocess.check_output(['git','-C',str(output/repo),'rev-list','--count','--all'],text=True).strip(),'1')
            finally:canary.unlink()

    def test_public_export_rejects_loopback_asset_pins(self):
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);pins=directory/'pins.json'
            pins.write_text(json.dumps({'releases':[{'assets':[{'url':'http://127.0.0.1:1/private-test'}]}]}))
            result=subprocess.run([sys.executable,str(ROOT/'scripts/prepare-public.py'),'--output',str(directory/'candidate'),'--release-pins',str(pins)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('development/credentialed',result.stderr)

if __name__=='__main__':unittest.main()
