#!/usr/bin/env python3
"""Actual CLI workflow acceptance plus bounded process ownership/fence probes."""
import json,os,signal,subprocess,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'scripts/run-workflow.py'
CLI=os.environ['AXIOM_CLI_PATH'];LSP=os.environ['ACORE_LSP_PATH']
PYTHON=os.environ.get('ACORE_PYTHON',os.sys.executable)
class Workflows(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='acore workflow ; punctuation ');self.root=Path(self.temp.name).resolve();(self.root/'AxiomDeps.toml').write_text('type = "frontend"\n')
  self.source=self.root/'a ; $(touch WRONG).acore';self.source.write_text('module editor.workflow.ui\napp EditorApp {route "/" => Home}\npage Home {view {Text("hello")}}\n');(self.root/'axiom.ui.lock.json').write_text('{"format":"axiom-ui-lock/v1","contracts":{}}')
  self.suite=self.root/'a suite ; $().json';self.suite.write_text(json.dumps({'format':'acore-application-test/v1','name':'real suite','cases':[{'name':'visible hello','steps':[{'do':'expect','query':{'text':'hello'},'count':1},{'do':'dispose'},{'do':'expect_clean'}]}]}));self.definition=self.root/'definition.json'
 def tearDown(self):self.temp.cleanup()
 def validate(self,workflow,inputs,code=0):
  r=subprocess.run([CLI,'editor','validate-workflow','--root',str(self.root),'--request',json.dumps({'workflow':workflow,'inputs':inputs})],capture_output=True,text=True,timeout=20);self.assertEqual(r.returncode,code,r.stdout+r.stderr);return json.loads(r.stdout) if not code else r.stderr
 def definition_for(self,workflow,inputs):self.definition.write_text(json.dumps({'type':'axiom-workflow','project':self.root.as_uri(),'workflow':workflow,'inputs':inputs}))
 def launch(self,cli=CLI,env=None,trust=True):
  return subprocess.Popen([PYTHON,str(RUNNER),'--root',str(self.root),'--cli',cli,'--definition',str(self.definition),*(['--trusted-workspace'] if trust else [])],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env={**os.environ,'ACORE_LSP':LSP,**(env or {})})
 def finished(self,p,code=0):
  stdout,stderr=p.communicate(timeout=40);self.assertEqual(p.returncode,code,stdout+stderr);return stdout+stderr
 def test_catalog_tracks_actual_cli_workflows(self):
  catalog=json.loads(subprocess.check_output([CLI,'editor','workflows','--json'],text=True));ids={w['id'] for w in catalog['workflows']};self.assertGreaterEqual(len(ids),193);self.assertTrue({'server/validate','server/package','server/dev','server/worker','ui/test','ui/host/install','database/runtime/prepare','database/fleet/prepare','database/fleet/recovery-check','editor/report'}<=ids,ids)
 def test_literal_argv_punctuation_choices_and_unsupported_options(self):
  v=self.validate('ui/test',{'source':self.source.name,'suite':self.suite.name,'target':'web','layer':'reference','report':'report ; $().json'});self.assertEqual(v['reportKind'],'application-assertions');self.assertEqual(v['argv'][-2:],["--",str(self.source)]);self.assertIn('--suite='+str(self.suite),v['argv']);self.assertFalse((self.root/'WRONG').exists())
  for inputs in [{'source':self.source.name,'typo':True},{'source':self.source.name,'layer':'invalid'},{'source':self.source.name,'suite':'../outside.json'},{'source':123}]:self.validate('ui/test',inputs,1)
  self.validate('build',{'file':'../outside.acore'},1)
  nested=self.root/'nested';nested.mkdir();(nested/'AxiomDeps.toml').write_text('type = \"frontend\"\n');(nested/'main.acore').write_text(self.source.read_text());self.validate('ui/test',{'source':'nested/main.acore'},1)
  self.validate('ui/test',{'source':self.source.name,'report':'--unsafe-output.json'});self.assertFalse((self.root/'WRONG').exists())
 def test_zed_runs_real_application_assertions_and_failure_reports(self):
  self.definition_for('ui/test',{'source':self.source.name,'suite':self.suite.name,'target':'web','layer':'reference','report':'acceptance report.json'});out=self.finished(self.launch());self.assertIn('Application suite assertions',out);self.assertRegex(out,r'[1-9][0-9]* assertions');self.assertTrue(json.loads((self.root/'acceptance report.json').read_text())['passed']);self.assertFalse((self.root/'WRONG').exists())
  suite=json.loads(self.suite.read_text());suite['cases'][0]['steps'][0]['count']=2;self.suite.write_text(json.dumps(suite));out=self.finished(self.launch(),1);self.assertIn('failed',out.lower());self.assertFalse(json.loads((self.root/'acceptance report.json').read_text())['passed'])
 def test_smoke_is_separate_and_trust_is_explicit(self):
  v=self.validate('ui/test',{'source':self.source.name,'target':'web'});self.assertEqual(v['reportKind'],'compiler-smoke');self.assertIn('zero application assertions',v['label']);self.definition_for('ui/test',{'source':self.source.name,'target':'web'});self.assertIn('requires suite',self.finished(self.launch(),1))
  self.definition_for('editor/report',{'entry':self.source.name,'root':str(self.root),'kind':'frontend','targets':['web'],'json':True});self.assertIn('trusted',self.finished(self.launch(trust=False),1));self.assertIn('axiom-editor-report/v1',self.finished(self.launch()))
 def probe_cli(self,mode):
  p=self.root/'probe-cli.py';p.write_text('''#!/usr/bin/env python3
import subprocess,sys,os,json,time
from pathlib import Path
real=os.environ['AXIOM_CLI_PATH'];mode=os.environ['PROBE_MODE']
if sys.argv[1:3] in [['editor','workflows'],['editor','validate-workflow']]:
 r=subprocess.run([real,*sys.argv[1:]],capture_output=True);sys.stdout.buffer.write(r.stdout);sys.stderr.buffer.write(r.stderr)
 if mode=='change' and sys.argv[2]=='validate-workflow':Path('changed.acore').write_text('changed = true')
 if mode=='change-bundle' and sys.argv[2]=='validate-workflow':Path('selected.bundle').write_text('changed = true')
 sys.exit(r.returncode)
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(300)']);Path('owned-child.pid').write_text(str(child.pid));time.sleep(300)
''');p.chmod(0o755);return str(p)
 def test_saved_input_fence_prevents_dispatch(self):
  self.definition_for('editor/report',{'entry':self.source.name,'root':str(self.root),'kind':'frontend','json':True});cli=self.probe_cli('change');self.assertIn('Saved inputs changed',self.finished(self.launch(cli,{'PROBE_MODE':'change'}),1));self.assertFalse((self.root/'owned-child.pid').exists())
 def test_selected_private_bundle_fence_prevents_dispatch(self):
  (self.root/'selected.bundle').write_text(self.source.read_text());self.definition_for('editor/report',{'entry':'selected.bundle','root':str(self.root),'kind':'frontend','json':True});self.assertIn('Saved inputs changed',self.finished(self.launch(self.probe_cli('change-bundle'),{'PROBE_MODE':'change-bundle'}),1));self.assertFalse((self.root/'owned-child.pid').exists())
 def test_cancellation_reaps_owned_descendants(self):
  self.definition_for('editor/report',{'entry':self.source.name,'root':str(self.root),'kind':'frontend','json':True});p=self.launch(self.probe_cli('cancel'),{'PROBE_MODE':'cancel'});end=time.monotonic()+20
  while not (self.root/'owned-child.pid').exists() and time.monotonic()<end:time.sleep(.05)
  self.assertTrue((self.root/'owned-child.pid').exists());child=int((self.root/'owned-child.pid').read_text());p.send_signal(signal.SIGTERM);self.finished(p,130)
  end=time.monotonic()+5
  while time.monotonic()<end:
   try:os.kill(child,0)
   except ProcessLookupError:break
   time.sleep(.05)
  else:self.fail('Owned descendant survived cancellation')
 def test_zed_template_quotes_and_saves_all_without_hooks(self):
  t=json.loads((ROOT/'templates/workflow-tasks.json').read_text())[0];self.assertEqual(t['save'],'all');self.assertFalse(t.get('hooks'));self.assertFalse(t.get('tags'));self.assertFalse(t['allow_concurrent_runs']);self.assertEqual(t['command'],'"$ACORE_PYTHON"');self.assertIn('ACORE_LSP',t['env']);self.assertTrue(all(a.startswith('"$') and a.endswith('"') for a in t['args'] if '$' in a))
if __name__=='__main__':unittest.main(verbosity=2)
