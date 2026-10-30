"""One explicitly root-granted label-only standalone52 cold native capture."""
import json,os,sys
import freeze_prepare_celeste_name_v1 as B
O=B.O;N=B.N;T=O/'native/cold-label-v1'
def main():
 assert sys.argv[1:]==['--launch']and not T.exists(),'Explicit one-run grant; no automatic retry.'
 p=json.loads((O/'native-prepared-v1.json').read_text());h=json.loads((O/'handoff.json').read_text())
 def verify():
  for d in [p,h]:
   for name,v in d['bindings'].items():assert B.B.sha(name)==v,name
  assert B.B.sha(N/'candidate.nes')==p['candidate']=='a7ccbaaa7aab598d36e8806e30475eab36174ee1948f25f90ae72e6640f43f48'
 verify();T.parent.mkdir(exist_ok=True);budget=B.Q.load(O/'native-capture-budget-v1.py');run=B.Q.run_function(budget)
 meta=dict(prepared=B.B.sha(O/'native-prepared-v1.json'),candidate=p['candidate'],bindings_verified=len(p['bindings'])+len(h['bindings']),config=p['config'])
 (O/'native-preflight-v1.json').write_text(json.dumps(meta,indent=2)+'\n');os.environ['SMB_RUN_OUTPUT']=str(T.resolve())
 rc=run(O/'native-driver-v1.lua',N/'candidate.nes',timeout=60,emulator_options=p['options']);verify()
 (O/'native-postflight-v1.json').write_text(json.dumps(dict(**meta,exit_code=rc,all_bindings_unchanged=True),indent=2)+'\n');print(json.dumps(dict(native_terminal=True,exit_code=rc,candidate=p['candidate'],output=str(T.resolve()),bindings_pass=True)),flush=True);raise SystemExit(rc)
if __name__=='__main__':main()
