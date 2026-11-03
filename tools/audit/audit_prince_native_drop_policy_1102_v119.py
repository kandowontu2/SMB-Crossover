"""Exact authenticated Prince native drop-hook effects and fixed suffix entry."""
from collections import Counter
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_game_loop_isr_1102_v102 as C
N,O=C.N,C.O


def main():
 b,seed,lab=C.loaded();at=C.C.C.I.location(b,'ShellOrBlockDefeat');pc=C.address(b,'ShellOrBlockDefeat');hook=C.address(b,'InventoryDropHook');code=b['raw'][at:at+6]
 assert code==bytes([0x20,hook&255,hook>>8,0xb5,C.address(b,'Enemy_ID'),0xc9])
 assert(at-16)//8192==126 and pc<0xa000 and seed.rawtags[0]==254
 inv=C.address(b,'InvDropEnemy');calls=Counter();tags=Counter();actual=N.NesMPU
 names=['InventoryDropHook','RlDropDispatch','InventoryEnemyDrop','InventoryLegacyClassic','DwCanDrop','RemainingCanDrop','NrCanDrop','HuCanDrop'];points={}
 for name in names:
  if name in b['syms']:points[C.address(b,name),((C.C.C.I.location(b,name)-16)//8192)|128]=name
 class Trace(actual):
  def step(self):
   if self.pc>=0x8000:
    tag=self.memory.rawtags[(self.pc-0x8000)//8192];name=points.get((self.pc,tag))
    if name:calls[name]+=1
    if self.pc==lab['PpNativeRoute']and tag==2:tags[self.memory[0x179]]+=1
   return super().step()
 N.NesMPU=Trace;rows=0;minimum=224
 try:
  for cwindow in [2,201]:
   for behavior in [0,1]:
    for slot in range(6):
     for ID in range(7):
      for random in [0,1,2,3]:
       m=N.fork(seed);N.put(m,CrossoverBehaviorVersion=behavior);m.raw_page(2,cwindow);N.put(m,CurrentBankC=cwindow)
       m[C.address(b,'Enemy_ID')+slot]=ID;m[C.address(b,'Enemy_Flag')+slot]=1;m[C.address(b,'Enemy_State')+slot]=0;m[C.address(b,'PseudoRandomBitReg')+1]=random;m[C.address(b,'PseudoRandomBitReg')+2]=255;m[inv]=0xa5
       before=bytes(m[:0x100])+bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);private=[bytes(z)for z in m.ram];smc=bytes(m[0x15a:0x17b]);maps=m.rawtags[:]
       out=N.invoke(m,'InventoryDropHook',a=83,x=slot,y=109,p=0xe1);minimum=min(minimum,out['minimum_SP']);assert(out['A'],out['X'],out['Y'])==(83,slot,109)and out['P']&0x6d==0xe1&0x6d,(cwindow,behavior,slot,ID,random,out)
       assert m[inv]==slot and maps==m.rawtags and private==[bytes(z)for z in m.ram],(m[inv],slot,maps,m.rawtags,[(k,hex(i),a,v)for k in range(4)for i,(a,v)in enumerate(zip(private[k],m.ram[k]))if a!=v][:8])
       assert all(0x15a+i in [0x162,0x16a,0x16c,0x16d,0x179]for i,(a,z)in enumerate(zip(smc,m[0x15a:0x17b]))if a!=z)
       m[inv]=0xa5;after=bytes(m[:0x100])+bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);assert before==after,('Unexpected native drop-hook effect',cwindow,behavior,slot,ID,random);rows+=1
 finally:N.NesMPU=actual
 q=dict(passed=True,CPU_only=True,ROM_written=False,proposal_only=True,current_memory_SHA256=C.C.C.image()[1]['expected_memory_only_SHA256'],cases=rows,C_windows=[2,201],behaviors=[0,1],native_slots=6,native_ID_domain=list(range(7)),drop_chance_low2bits=[0,1,2,3],hook_calls=dict(calls),actual_owner_tags=dict(tags),only_native_effect=dict(symbol='InvDropEnemy',address=inv,value='Actual input native slotX'),all_AXY_exact=True,returned_NZ='Native FarCallCommon final LDA83 sets N0/Z0; suffix LDAEnemyID/CMP13 overwrites those flags before use in admittedID0..6 domain.',full_private_ZP_R0_R7_mapper_and_other_native_fields_exact=True,SMC='Only five declared foreground transport operands may change during the original call/top-level fixture. The enclosing native gateway restores allfive from its existing13B packet; no other SMC/code byte changes.',minimum_SP=minimum,original_fixed_native_defeat_entry=pc,original_first_JSR_bytes=code[:3].hex(),suffix_entry=pc+3,suffix_first_bytes=code[3:].hex(),source_scope='Private outer source guard admission already authenticates both headers and restricts native IDs0..6/flag1/stateNot32; original native Piranha13 ADC branch is excluded. Current native RemainingChooseAmmo rejects raw38 before reaching any Prince callback; all actual owner tags are empty. This receipt measures a possible authenticated owned acknowledgement, not approval to skip any call or change foreign/native routines.',bindings={p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),O/'post-return-manifest-v97.json',R/'src/inventory_drops.s',R/'src/collision.s',R/'src/remaining_weapons.s',R/'src/darkwing_pickups.s',R/'src/roll_dispatch.s',O/'native-public-v78.s',O/'current-earned-defeat-negative-v114.json']})
 (O/'native-drop-policy-CPU-v119.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'native-drop-policy-negative-v119.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
