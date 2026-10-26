"""Reuse immutable source checker through each role's first proven recurrence."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):assert not p.exists();p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();o=a.packet/'full-call-recurrences-v1';o.mkdir(exist_ok=False)
 source=D/'smb3-original-music-closure-v3/proof.json';roles=json.loads(source.read_text())['roles'];rows=[];checker=R/'tools/audit/smb3_native_core_cpu_v3.py'
 for role,source_role in roles.items():
  last=source_role['exact_call_boundary_state_repeat']['repeat_tick'];pair={}
  for side,rom in [('parent',D/'smb3-native-core-v5/candidate.nes'),('candidate',a.packet/'candidate.nes')]:
   cmd=[sys.executable,str(checker),'--rom',str(rom),'--output',str(o/(role+'-'+side)),'--role',role,'--calls',str(last)]
   run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/(role+'-'+side+'.launch.json'),dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,(role,side,run.stdout,run.stderr)
   proof=json.loads((o/(role+'-'+side)/'proof.json').read_text());assert proof['passed'];pair[side]=proof['roles'][0]
  old,new=pair['parent'],pair['candidate']
  for name in ['role','song','calls','ordered_original_APU_stores','physical_APU_stores','source_state_digest','physical_DMC_sample_checks','distinct_DMC_configs','DMC_payload_union_bytes','samples']:assert old[name]==new[name],(role,name,old[name],new[name])
  assert new['mean_play_cycles']<old['mean_play_cycles']and new['peak_play_cycles']<old['peak_play_cycles']and new['init_cycles']<old['init_cycles']
  row=dict(role=role,calls=new['calls'],state_recurrence=source_role['exact_call_boundary_state_repeat'],ordered_APU_stores=new['ordered_original_APU_stores'],DMC_source_payload_checks=new['physical_DMC_sample_checks'],old_mean=old['mean_play_cycles'],new_mean=new['mean_play_cycles'],saved_mean=old['mean_play_cycles']-new['mean_play_cycles'],old_peak=old['peak_play_cycles'],new_peak=new['peak_play_cycles'],old_cold=old['init_cycles'],new_cold=new['init_cycles']);rows.append(row);print(json.dumps(row),flush=True)
 put(o/'proof.json',dict(passed=True,source_only=True,native_run=False,host_integration=False,ROM_sha256=sha(a.packet/'candidate.nes'),parent_ROM_sha256=sha(D/'smb3-native-core-v5/candidate.nes'),source_proof_sha256=sha(source),checker_sha256=sha(checker),tool_sha256=sha(__file__),roles=rows,calls_per_ROM=sum(r['calls']for r in rows),ordered_APU_stores_per_ROM=sum(r['ordered_APU_stores']for r in rows),DMC_source_payload_checks_per_ROM=sum(r['DMC_source_payload_checks']for r in rows),same_source_state_digests_ordered_stores_samples_and_registers=True,scope='Exact12 fixed cold roles, each through first original call-boundary recurrence; no rerun of old18000play suffix or host/NMI/native qualification. Original full18k evidence stays old-a4be only.'))
if __name__=='__main__':main()
