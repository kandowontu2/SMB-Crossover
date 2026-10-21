"""Fresh current-ROM attempts using historical controller polls as inputs only."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BASE=ROOT/'build/roster-through-2-2'
OUT=ROOT/'build/verification/current47-extra-replays-a'
ROM=ROOT/'build/checkpoints/roster-audit-v47/smb-crossover-mmc3.nes'
CASES=(
 ('Link',4,'lsr-v34-link-fixed-full-audit-a-4-v0-mmc3'),
 ('Simon',5,'lsr-v34-simon-fixed-full-audit-a-5-v0-mmc3'),
 ('Pit',6,'pit-38d-full-audit-a-6-v0-mmc3'),
 ('Rygar',7,'rygar-38d-full-audit-a-7-v0-mmc3'),
)
def main():
 assert not OUT.exists()
 assert sha(ROM)=='e9c1a98961d26389bc54eefc4c63e725f8ddd91c0e801cf9c553bdf774ece1f1'
 plan=[]
 for name,char,folder in CASES:
  p=BASE/folder;manifest=json.loads((p/'manifest.json').read_text())
  assert manifest['controller_only']and not manifest['memory_or_register_writes']
  assert manifest['full_frame_audit']
  assert manifest['verified_through_2_2']and manifest['result']['all_six_stages']and manifest['result']['cleared']
  assert manifest['inputs_sha256']==sha(p/'inputs.csv')
  tag='root47-'+name.lower()+'-replay-a'
  assert not(BASE/f'{tag}-{char}-v0-mmc3').exists()
  plan.append(dict(character=name,character_id=char,source=str(p.relative_to(ROOT)),
   historical_manifest_sha256=sha(p/'manifest.json'),inputs_sha256=sha(p/'inputs.csv'),
   source_ROM_hash=manifest['rom_sha256'],tag=tag,frame_bound=manifest['result']['frames']+10))
 OUT.mkdir();(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 report=dict(result='running',scope='Fresh ordinary power-on replay attempts, no recordings. Historical clears supply controller input only; current audit is authoritative.',
  ROM_sha256=sha(ROM),plan_sha256=sha(OUT/'plan.json'),runner_sha256=sha(ROOT/'tools/playthroughs/roster_run.py'),runs=[])
 rp=OUT/'report.json'
 def save():rp.write_text(json.dumps(report,indent=2)+'\n')
 save()
 for r in plan:
  source=ROOT/r['source'];assert sha(source/'inputs.csv')==r['inputs_sha256']
  cmd=[sys.executable,'tools/playthroughs/roster_run.py','--character',str(r['character_id']),
   '--mapper','mmc3','--rom',str(ROM),'--tag',r['tag'],'--replay',str(source/'inputs.csv'),
   '--frames',str(r['frame_bound']),'--timeout','300']
  log=OUT/(r['character'].lower()+'.log');print('START',r['character'],flush=True)
  with log.open('w')as f:result=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  path=BASE/f"{r['tag']}-{r['character_id']}-v0-mmc3"/'manifest.json'
  actual=json.loads(path.read_text())if path.exists()else{}
  report['runs'].append(dict(character=r['character'],character_id=r['character_id'],command=cmd,exit=result.returncode,
   log=str(log.relative_to(ROOT)),log_sha256=sha(log),manifest=str(path.relative_to(ROOT)),
   manifest_sha256=sha(path)if path.exists()else None,verified_through_2_2=actual.get('verified_through_2_2',False),result=actual.get('result')))
  save();print('END',r['character'],result.returncode,actual.get('verified_through_2_2',False),flush=True)
 report['result']='all-four-current47-pass'if all(r['verified_through_2_2']for r in report['runs'])else'partial-results-preserved'
 save();print(report['result'],flush=True)
if __name__=='__main__':main()
