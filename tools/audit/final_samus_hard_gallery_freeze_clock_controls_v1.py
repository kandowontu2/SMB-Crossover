"""Actual full freeze caller/borrow/leaf/return proof; no emulator launch."""
from pathlib import Path
import argparse,hashlib,json
import final_samus_hard_gallery_source_v1 as source
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA,PARENT,TraceArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def controls(b):
 active=None
 owner=(address(b,'RemainingWeapons::Freeze'),(location(b,'RemainingWeapons::Freeze')-16)//8192)
 leaf=(address(b,'SamusFrozenDecrement'),(location(b,'SamusFrozenDecrement')-16)//8192)
 if 'RemainingWeapons::Freeze'not in source.OWNER_NAMES:source.OWNER_NAMES.append('RemainingWeapons::Freeze')
 class Spy(NesMPU):
  def step(c):
   q=active;bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   def timer():return q.get('AvFrozen')+256*q.get('AvFrozenHi')
   if q.pending and(c.pc,bank,c.sp)==tuple(q.pending['return']):
    z=q.pending;z['after']=timer();z['returned']=dict(pc=c.pc,bank=bank,sp=c.sp,a=c.a,x=c.x,y=c.y,p=c.p);assert z['before']>0 and z['after']==z['before']-1;q.clock.append(z);q.pending=None
   if(c.pc,bank)==owner and c.x==0:q.full_before=timer()
   if(c.pc,bank)==leaf and c.x==0:
    ret=(q.m[0x100+((c.sp+1)&255)]+256*q.m[0x100+((c.sp+2)&255)]+1)&65535;rb=q.m.banks[(ret-0x8000)//8192]if ret>=0x8000 else-1
    q.pending=dict(before=q.full_before,leaf_partial=timer(),leaf_entry=dict(pc=c.pc,bank=bank,sp=c.sp),return_=[ret,rb,(c.sp+2)&255]);q.pending['return']=q.pending.pop('return_');assert timer()==q.full_before-(256 if q.full_before%256==0 else 0)
   return super().step()
 saved=source.NesMPU;source.NesMPU=Spy;rows=[]
 def initialize(q):
  q.clock=[];q.pending=None;q.full_before=None;q.set('InvOwnedLo',137,2);q.put(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=130,Enemy_PageLoc=1,Enemy_Y_Position=150,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9)
 try:
  for value in[0,1,2,255,256,257,359,360,511,512,65535]:
   q=TraceArena(b);active=q;initialize(q);q.put(AvFrozen=value&255,AvFrozenHi=value>>8,RgEnemyStun=255,LsrFrozenPose=1);q.invoke('ProcFireball_Bubble');after=q.get('AvFrozen')+256*q.get('AvFrozenHi');assert after==max(0,value-1)and len(q.clock)==bool(value)and q.pending is None
   if value==1:assert q.get('RgEnemyStun')==q.get('LsrFrozenPose')==0
   rows.append(dict(value=value,after=after,clock=q.clock,calls=q.calls))
  # One genuine source Ice emission/contact creates its own360 timer, then
  # complete native dispatches count down to0 with no timer reseeding.
  q=TraceArena(b);active=q;initialize(q);q.put(Enemy_Flag=0,A_B_Buttons=64,PreviousA_B_Buttons=0);q.invoke('ProcFireball_Bubble')
  for _ in range(3):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
  world=q.get('RgShotX',9)+256*q.get('RgShotPage',9)-6
  q.put(Enemy_Flag=1,Enemy_X_Position=world&255,Enemy_PageLoc=world>>8,Enemy_Y_Position=q.get('RgShotY',9)-8);q.invoke('ProcFireball_Bubble');assert q.get('AvFrozen')+256*q.get('AvFrozenHi')==360
  q.clock=[]
  for _ in range(360):q.put(A_B_Buttons=0,InvFresh=0);q.invoke('ProcFireball_Bubble')
  assert len(q.clock)==360 and[q['before']for q in q.clock]==list(range(360,0,-1))and q.get('AvFrozen')==q.get('AvFrozenHi')==q.get('RgEnemyStun')==q.get('LsrFrozenPose')==0
  episode=dict(clock=q.clock,calls=q.calls,borrow=next(z for z in q.clock if z['before']==256),thaw=q.clock[-1])
 finally:source.NesMPU=saved
 return dict(passed=True,source_only=True,ROM_sha256=SHA,complete_gateway_cells=11,genuine_emission_contact_and_360_complete_updates=True,seeded_boundary_cells=rows,source_created_episode=episode,native_operand_dump=False,scope='CPU source trace supplies before256/leaf-partial0/after255 at actualAB80. Old native did not dump raw timer operands; its freeze creation/update distance/PC/A are consistent, not backfilled.')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA;z=controls(b);put(a.output/'proof.json',z);print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),cells=z['complete_gateway_cells'],borrow=z['source_created_episode']['borrow'])))
if __name__=='__main__':main()
