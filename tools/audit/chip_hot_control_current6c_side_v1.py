"""Strict old/new side caller differential, including unchanged foreign admissions."""
from pathlib import Path
import argparse,hashlib,json
from chip_hot_control_cpu_v2 import D,setup,clone,run,compare,phys
from check_tmnt_render_oa import load,address
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=load(a.parent);new=load(a.candidate);f=D/'chip-idle-profiler-v1/fixture-v4';ss=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];raw=(f/'profile-snapshots.ram').read_bytes();cfg=json.loads((f/'configuration.json').read_text());s=next(x for x in ss if x['kind']=='component-entry'and x['detail']=='GameLoop');m,c=setup(old,s,raw,cfg);states=[]
 for _ in range(100000):
  if c.pc==address(old,'MmNativeSideShortcut'):
   mm,cc=clone(old,m,c);states.append((mm,cc))
  c.step()
  if len(states)==4:break
 else:raise AssertionError('four original side admissions absent')
 cases=[]
 for ix,(m,c)in enumerate(states):
  for char in range(21):
   for variant in range(2):
    om,oc=clone(old,m,c);nm,nc=clone(new,m,c)
    for b,mem in[(old,om),(new,nm)]:mem[address(b,'SelectedCharacter')]=char;mem[address(b,'Z2Variant')]=variant
    ot=run(om,oc);nt=run(nm,nc);q=compare(om,nm,oc,nc);q.update(selected=char,Z2Variant=variant,actual_side_input=ix,old_cycles=ot,new_cycles=nt,delta=nt-ot);cases.append(q)
 proof=dict(passed=all(q['passed']for q in cases),native_executed=False,ROM_sha256=sha(a.candidate),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),scope='Source/CPU side-component differential on four captured actual Chip query inputs, varying exact selector0..20 and Z2Variant0/1 only. This is not authentic foreign full-game movement/state coverage.',cases=len(cases),failures=[q for q in cases if not q['passed']],foreign_all_pass=all(q['passed']for q in cases if q['selected']!=14),foreign_max_cycle_delta=max(q['delta']for q in cases if q['selected']!=14),foreign_min_cycle_delta=min(q['delta']for q in cases if q['selected']!=14),checker_sha256=sha(__file__))
 (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='failures'},indent=2))
if __name__=='__main__':main()
