"""Run exactly one specifically bound, root-granted native FF class."""
from pathlib import Path
import argparse,json,os,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
import arthur_body_fair_budget_v7 as Q
def main():
 a=argparse.ArgumentParser();a.add_argument('--packet',type=Path,required=True);a.add_argument('--launch',required=True);v=a.parse_args();F=v.packet.resolve()
 p=json.loads((F/'prepared.json').read_text());h=json.loads(Path(p['source_handoff_path']).read_text());J=Path(p['joint']);name=v.launch
 assert name in p['classes'];target=Path(p['output'])/(name+'-cold-v3');assert not target.exists()
 def verify():
  for d in[p,h]:
   for f,x in d['bindings'].items():assert B.sha(f)==x,f
  assert B.sha(J/'candidate.nes')==p['candidate'] and B.sha(p['source_handoff_path'])==p['source_handoff']
 verify();active=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process -Filter \"Name = 'Mesen.exe'\" | Select-Object -ExpandProperty ProcessId"],capture_output=True,text=True,check=True)
 assert not active.stdout.strip(),'Existing Mesen belongs to user/another run; do not launch or touch it: '+active.stdout
 meta=dict(candidate=p['candidate'],source_handoff=p['source_handoff'],class_name=name,prepared_sha256=B.sha(F/'prepared.json'),bindings_verified=sum(len(d['bindings'])for d in[p,h]),configuration=p['configuration'],no_existing_Mesen=True)
 (F/(name+'-preflight.json')).write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8',newline='\n')
 run=Q.run_function(Q.load(F/'capture-budget.py'));os.environ['SMB_RUN_OUTPUT']=str(target)
 rc=run(F/(name+'.lua'),J/'candidate.nes',emulator=p['emulator'],timeout=120,emulator_options=p['options'])
 verify();(F/(name+'-postflight.json')).write_text(json.dumps(dict(**meta,exit_code=rc,all_pre_post_bindings_exact=True),indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(native_terminal=True,exit_code=rc,candidate=p['candidate'],class_name=name,output=str(target),bindings_pass=True)),flush=True);raise SystemExit(rc)
if __name__=='__main__':main()
