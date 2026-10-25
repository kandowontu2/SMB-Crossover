"""Actual linked signed-window helper and full crate-contact admission checks."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,address
from kirby_chip_audit_cpu_v1 import Arena
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','rom','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(exist_ok=False);old,new=load(a.baseline),load(a.rom)
 helper=0;negative=0;contacts=0;exact=0
 q=Arena(new,'CdContactYWindow',{})
 for slot in [0,3]:
  for y,crate in itertools.product(range(256),range(240)):
   q.m[address(new,'Enemy_Y_Position')+slot]=y;q.m[address(new,'Enemy_Y_HighPos')+slot]=1;q.put(CdRectY=crate)
   c,_,_=q.run('CdContactYWindow',x=slot)
   assert bool(c.p&1)==(-16<=y+8-crate<16),(slot,y,crate,c.p)
   assert c.x==slot and c.y==0
   helper+=1
  for high,y,crate in itertools.product([0,2,255],range(256),[0,1,8,12,16,24,32,64,128,192,224,239]):
   q.m[address(new,'Enemy_Y_Position')+slot]=y;q.m[address(new,'Enemy_Y_HighPos')+slot]=high;q.put(CdRectY=crate)
   c,_,_=q.run('CdContactYWindow',x=slot);assert not c.p&1;negative+=1
 for variant,crate,gap in itertools.product([0,1],[0,1,8,12,32,64,128,200,239],[-17,-16,-1,0,15,16]):
  y=crate+gap-8
  if not 0<=y<256:continue
  def arena(b):return Arena(b,'CdBoxEnemies',dict(SelectedCharacter=14,CdVariant=variant,CdSlot=0,CdBoxKind=[1],CdBoxMode=[2],CdBoxX=[100],CdBoxPage=[0],CdBoxY=[crate],Enemy_Flag=[1],Enemy_ID=[6],Enemy_State=[0],Enemy_X_Position=[100],Enemy_PageLoc=[0],Enemy_Y_Position=[y],Enemy_Y_HighPos=[1],ObjectOffset=4))
  oq,nq=arena(old),arena(new)
  oc,os,_=oq.run('CdBoxEnemies',traps=['CdDefeatEnemy']);nc,ns,_=nq.run('CdBoxEnemies',traps=['CdDefeatEnemy'])
  allowed=-16<=gap<16
  assert bool(ns)==allowed and(nq.get('CdBoxKind')==0)==allowed
  contacts+=1
  if allowed:
   assert bool(os)
   # Full contact routine; only hardware stack differs due to added helper.
   diff=[i for i in range(0x8000)if not 0x100<=i<0x200 and oq.m[i]!=nq.m[i]]
   assert not diff,diff[:10]
   assert(oc.a,oc.x,oc.y,oc.p,oc.sp)==(nc.a,nc.x,nc.y,nc.p,nc.sp)
   exact+=1
 proof=dict(passed=True,private=True,adopted=False,goal_complete=False,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),baseline_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),all_visible_y_pairs_two_slots=helper,foreign_page_negatives=negative,full_contact_boundary_cases=contacts,valid_contact_exact_application_RAM_registers_flags_stackdepth=exact,scope='Actual linked helper for every enemy lowY/visible crateY pair, slots0/3, and full admission boundary controls for both alternates. CdDefeatEnemy intercepted only at its actual entry to identify admission; no mocked defeat effect. Native effects covered separately. Only hardware-stack contents excluded from full valid-contact RAM differential.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
if __name__=='__main__':main()
