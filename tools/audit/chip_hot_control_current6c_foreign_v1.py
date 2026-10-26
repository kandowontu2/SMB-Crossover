"""Foreign movement continuation ABI at the unchanged authentic callee entries."""
from pathlib import Path
import argparse,hashlib,itertools,json
from chip_hot_control_cpu_v2 import D,setup,clone,phys
from check_tmnt_render_oa import load,address,location
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def state(m,c):return(c.pc,c.a,c.x,c.y,c.p,c.sp,bytes(m[:0x800])+bytes(m[0x5c00:0x8000]),tuple(m.banks))
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=load(a.parent);new=load(a.candidate);f=D/'chip-idle-profiler-v1/fixture-v4';ss=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];raw=(f/'profile-snapshots.ram').read_bytes();cfg=json.loads((f/'configuration.json').read_text());s=next(x for x in ss if x['kind']=='component-entry'and x['detail']=='GameLoop');m,c=setup(old,s,raw,cfg)
 for _ in range(100000):
  if c.pc==address(old,'X5OwnMovement')and phys(m,c.pc)==86:break
  c.step()
 else:raise AssertionError('movement caller absent')
 cases=0;deltas=set()
 for char,av,pv in itertools.product([i for i in range(21)if i!=14],[0,14,255],range(256)):
  pairs=[]
  for b in[old,new]:
   mm,cc=clone(b,m,c);cc.a=av;cc.p=pv;mm[address(b,'SelectedCharacter')]=char;name='TnMovement'if char==19 else'LmMovementGate';pc=address(b,name);bank=(location(b,name)-16)//8192
   for _ in range(1000):
    if cc.pc==pc and phys(mm,cc.pc)==bank:break
    cc.step()
   else:raise AssertionError(('foreign entry timeout',char,av,pv))
   pairs.append((state(mm,cc),cc.processorCycles))
  assert pairs[0][0]==pairs[1][0],('foreign authentic entry ABI changed',char,av,pv)
  cases+=1;deltas.add(pairs[1][1]-pairs[0][1])
 assert deltas=={7},deltas
 proof=dict(passed=True,native_executed=False,ROM_sha256=sha(a.candidate),parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),foreign_private_entry_cases=cases,all256_input_P_values=True,input_A_values=[0,14,255],selected=list(i for i in range(21)if i!=14),exact_real_callee_entry_AXYPS_RAM_including_stack_and_SMC_banks=True,cycles_at_entry_extra=7,unchanged_callee_code=True,camera_padding_old_cycles=30,camera_jump_new_cycles=3,whole_foreign_movement_delta=-20,scope='Compositional CPU continuation proof. Every foreign actual movement leaf is byte-identical and entered with exact complete CPU/RAM/SMC/stack/bank state; after its return the genuine camera wrapper saves27NOP cycles, offsetting7 added admission cycles. No native clock/IRQ/NMI timing claim and no new full foreign playthrough.',checker_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
