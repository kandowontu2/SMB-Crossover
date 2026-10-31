"""Run one root-granted corrected FF cold fixture; refuse interactive Mesen."""
from pathlib import Path
import json,os,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
import arthur_body_fair_budget_v7 as Q
O=R/'build/ff-cold-preview-v5';J=O/'joint';F=O/'native-prepared-v2'
def main():
 assert len(sys.argv)==3 and sys.argv[1]=='--launch','Requires separate root one-run grant.'
 p=json.loads((F/'prepared.json').read_text());h=json.loads((O/'handoff-source-v1.json').read_text())
 name=sys.argv[2];assert name in p['classes'];target=O/'native'/(name+'-cold-v2');assert not target.exists()
 def verify():
  for d in[p,h]:
   for f,v in d['bindings'].items():assert B.sha(f)==v,f
  assert B.sha(J/'candidate.nes')==p['candidate']==h['candidate']
  assert B.sha(O/'handoff-source-v1.json')==p['source_handoff']
 verify()
 active=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name = 'Mesen.exe'\" | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
 assert not active.stdout.strip(),'Existing Mesen belongs to user/another run; do not launch or touch it: '+active.stdout
 meta=dict(candidate=p['candidate'],source_handoff=p['source_handoff'],class_name=name,prepared_sha256=B.sha(F/'prepared.json'),bindings_verified=sum(len(d['bindings'])for d in[p,h]),configuration=p['configuration'],options=p['options'],emulator=p['emulator'],no_existing_Mesen=True)
 (F/(name+'-preflight.json')).write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
 budget=Q.load(F/'capture-budget.py');run=Q.run_function(budget);os.environ['SMB_RUN_OUTPUT']=str(target.resolve())
 rc=run(F/(name+'.lua'),J/'candidate.nes',emulator=p['emulator'],timeout=120,emulator_options=p['options'])
 verify();(F/(name+'-postflight.json')).write_text(json.dumps(dict(**meta,exit_code=rc,all_pre_post_bindings_exact=True),indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(native_terminal=True,exit_code=rc,candidate=p['candidate'],class_name=name,output=str(target.resolve()),bindings_pass=True)),flush=True)
 raise SystemExit(rc)
if __name__=='__main__':main()
