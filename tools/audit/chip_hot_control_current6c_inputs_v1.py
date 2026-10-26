"""Finite complete-caller CPU controls from actual captured Chip entry states."""
from pathlib import Path
import argparse,hashlib,itertools,json
from chip_hot_control_cpu_v2 import D,setup,clone,run,compare,phys
from check_tmnt_render_oa import load,address
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=load(a.parent);new=load(a.candidate);f=D/'chip-idle-profiler-v1/fixture-v4';ss=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];raw=(f/'profile-snapshots.ram').read_bytes();cfg=json.loads((f/'configuration.json').read_text());states=[]
 for s in[x for x in ss if x['kind']=='component-entry'and x['detail']=='GameLoop'][:4]:
  m,c=setup(old,s,raw,cfg)
  for _ in range(100000):
   if c.pc==address(old,'PlayerCtrlRoutine')and phys(m,c.pc)==1:break
   c.step()
  else:raise AssertionError('no player control')
  states.append((m,c))
 controls=[0,1,2,4,8,16,32,64,128,0x81,0x41,0xc1,0x82,0x42,0xc2,0x84];cases=[]
 for ix,(m,c)in enumerate(states):
  for mode,water,buttons in itertools.product(range(2),range(2),controls):
   om,oc=clone(old,m,c);nm,nc=clone(new,m,c)
   for b,mem in[(old,om),(new,nm)]:
    for n,v in dict(CrossoverBehaviorVersion=mode,SwimmingFlag=water,AreaType=0 if water else 1,SavedJoypadBits=buttons).items():mem[address(b,n)]=v
   ot=run(om,oc);nt=run(nm,nc);q=compare(om,nm,oc,nc);q.update(snapshot=ix,numeric_mode=mode,water=water,buttons=buttons,old_cycles=ot,new_cycles=nt,delta=nt-ot);cases.append(q)
 proof=dict(passed=all(q['passed']for q in cases),native_executed=False,ROM_sha256=sha(a.candidate),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),cases=len(cases),minimum_cycle_delta=min(q['delta']for q in cases),maximum_cycle_delta=max(q['delta']for q in cases),failed_cases=[q for q in cases if not q['passed']],scope='256 actual assembled full PlayerCtrl CPU caller differentials: four captured states, Easy/Hard numeric0/1, land/water area flags and16 controller masks. All applicationRAM/copiedSMC/fullAXYPS/mapper banks exact; inactive stack discarded. Controlled CPU arenas, not native scene/traversal/swimming certification.',checker_sha256=sha(__file__))
 (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='failed_cases'},indent=2))
if __name__=='__main__':main()
