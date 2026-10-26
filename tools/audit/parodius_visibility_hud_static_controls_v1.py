"""Prepare/run only the seven explicitly granted static df515 cold controls."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','run']);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--parser-root',type=Path);p.add_argument('--emulator',type=Path);a=p.parse_args()
 if a.action=='prepare':
  assert a.parser_root;a.output.mkdir(parents=True,exist_ok=False);profiles=[]
  names=['octopus-easy','pentarou-easy','octopus-hard','twinbee-hard','pentarou-hard','vic-easy','vic-hard']
  for name in names:
   original=a.parent/('hud-scroll-native-initial-v1'if name=='octopus-easy'else'hud-scroll-native-remaining-v1')/name;packet=a.output/name;cmd=[sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_hud_static_prepare_v1.py'),'--parent',str(original),'--output',str(packet),'--parser-root',str(a.parser_root)];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;z=json.loads((packet/'preparation.json').read_text());profiles.append(dict(name=name,packet=str(packet.resolve()),original=str(original.resolve()),mode=z['mode'],variant=z['variant'],preparation_sha256=sha(packet/'preparation.json')))
  q=dict(prepared=True,native_qualified=False,ROM_sha256='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357',profiles=profiles,tool_sha256=sha(Path(__file__)),scope='Only7 controls explicitly granted after Twin static diagnostic: first whole OctEasy observation equivalence, then remaining6 cold640 modes/variants. ONE sequential worker, stop on any failure/no retry.')
  (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(profiles=7,preparation_sha256=sha(a.output/'preparation.json'))));return
 assert a.emulator and not(a.output/'proof.json').exists();z=json.loads((a.output/'preparation.json').read_text());rows=[];stop=False
 for profile in z['profiles']:
  if(a.output/'STOP').exists():stop=True;break
  packet=Path(profile['packet']);assert sha(packet/'preparation.json')==profile['preparation_sha256'];prep=json.loads((packet/'preparation.json').read_text());out=Path(prep['script']).parent;print('START '+profile['name'],flush=True)
  r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_hud_scroll_native_run_v1.py'),'--packet',str(packet),'--emulator',str(a.emulator)],capture_output=True,text=True);(packet/'control-runner-host.log').write_text(r.stdout+r.stderr,encoding='utf-8');proof=out/'scroll-proof.json';native=json.loads(proof.read_text())if proof.exists()else{};row=dict(profile,passed=r.returncode==0 and native.get('passed',False),runner_exit=r.returncode,proof_sha256=sha(proof)if proof.exists()else None)
  if row['passed']and profile['name']=='octopus-easy':
   compare=a.output/'octopus-whole-equivalence-v1';c=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/parodius_visibility_hud_static_equivalence_v1.py'),'--original',profile['original'],'--replay',str(packet),'--output',str(compare)],capture_output=True,text=True);(compare/'host.log').write_text(c.stdout+c.stderr,encoding='utf-8');f=compare/'proof.json';row.update(passed=c.returncode==0,equivalence_proof_sha256=sha(f)if f.exists()else None,equivalence_exit=c.returncode)
  if row['passed']:
   assert native['original_guards']['actual_mode']==profile['mode']and native['original_guards']['actual_variant']==profile['variant'];frames=[json.loads(s)for s in(out/'hud-frames.jsonl').read_text().splitlines()];row.update(native=native['original_guards']['native'],HUD=native['original_guards']['HUD'],scroll=native['scroll'],first_HUD_active_frame=next((v['finished']['frame']for v in frames if v['start']['ram']['InvHudActive']),None))
  rows.append(row);print(json.dumps(dict(name=row['name'],passed=row['passed'],proof_sha256=row['proof_sha256'],equivalence=row.get('equivalence_proof_sha256'),first_HUD=row.get('first_HUD_active_frame'))),flush=True)
  if not row['passed']:break
 q=dict(native_assertions_passed=len(rows)==7 and all(v['passed']for v in rows),passed=False,PPU_RGB_review_complete=False,goal_complete=False,ROM_sha256=z['ROM_sha256'],preparation_sha256=sha(a.output/'preparation.json'),tool_sha256=sha(Path(__file__)),profiles=rows,stopped_by_owner_file=stop,scope='Only7 explicitly granted static-observer controls; first whole OctEasy equality then remaining6. Stop on any failure; no automatic retry/lifecycle/body trial. Fresh offline visual/RGB aggregation still needed.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(profiles=len(rows),native_assertions_passed=q['native_assertions_passed'],proof_sha256=sha(a.output/'proof.json'))));raise SystemExit(0 if q['native_assertions_passed']else 1)

if __name__=='__main__':main()
