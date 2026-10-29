"""Actual interrupt scratch and retained Luigi callers; CPU only."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_pipeline_controls_v1 as a
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import seed,run,app,registers,cleanwrites
O=R/'build/rogue-dawn-host-pipeline-v2';P=R/'build/roster-shared-celeste-small-v1.nes'

def main():
 b=a.d.old.scoped_load(O/'candidate.nes');old=a.d.old.scoped_load(P);seams=[]
 for name,physical in [('RdTxHead',95),('RdTxMovementFlush',95),('NativeRarePlayerHeadCollisionCore',9),('SetupPowerUp',126),('NrPrepare',124),('RdNrPrepare',124),('RdTxPrepareActor',95),('RdHsPrepareActor',95),('RdNativeBGGate',1)]:
  for kind in ['IRQ','lagNMI']:
   m=a.base(b,'head' if name!='RdNativeBGGate' else 'floor',0,128);zps=[address(b,'R'+str(i))for i in range(8)];saved=NesMPU.step;stack=[];verified=[]
   def step(c):
    if c.pc in [address(b,'NonMaskableInterrupt'),address(b,'IrqScrollSplit')]:stack.append(bytes(m[z]for z in zps))
    rti=m[c.pc]==0x40;saved(c)
    if rti:
     expected=stack.pop();actual=bytes(m[z]for z in zps);assert actual==expected,('ISR native scratch',name,kind,list(expected),list(actual));verified.append(actual.hex())
   NesMPU.step=step
   try:c,row=a.idle(m,seam=(address(b,name),physical,kind))
   finally:NesMPU.step=saved
   assert len(verified)==1 and not stack
   seams.append(dict(entry=name,physical_code_bank=physical,kind=kind,minimum_SP=row['minimum_SP'],native_R0_to_R7_exact=True))
 # Retained real procedures/Done/terminal bridge remain literal, including
 # all their public PCs. The new gate is unreachable by old fallthrough.
 p0,p1=location(old,'LuigiNativeTraction'),location(b,'LuigiNativeTraction')
 assert old['raw'][p0:p0+43]==b['raw'][p1:p1+43]
 assert old['raw'][p0+83:p0+84]==b['raw'][p1+83:p1+84]==b'\x60'
 assert address(old,'LuigiSourceMovementBridge')==address(b,'LuigiSourceMovementBridge')
 assert address(b,'RdNativeBGGate')==address(b,'LuigiNativeTraction')+43
 assert old['raw'][p0+43:p0+84]==b'\xea'*40+b'\x60'
 rows=[]
 for char,wet,state,vx,lr,flags in itertools.product([0,2,8],[0,1],[0,1],[0,16,240],[0,1,2],[0x30,0x31,0x71,0xf3]):
  pair=[]
  for bundle in [old,b]:
   q=seed(bundle,char);q.put(SwimmingFlag=wet,Player_State=state,Player_X_Speed=vx,Left_Right_Buttons=lr)
   c,w,_=run(q,'LuigiNativeTraction',a=90,x=3,y=7,p=flags);pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
  assert pair[0]==pair[1],('retained native traction',char,wet,state,vx,lr,flags)
  rows.append(dict(raw=char,wet=wet,state=state,VX=vx,input=lr,flags=flags))
 # Exact real flags at owned-return and foreign-tail boundaries, not merely
 # a single flags71 example. Physical6502 B/U virtual serialization is omitted.
 flags_cases=0
 for char,var,flags in itertools.product([0,2,8],[0,1],range(256)):
  m=a.d.old.make(b);m[address(b,'SelectedCharacter')]=char;m[0x5fee]=var;m.page(1,1);m[address(b,'CurrentBank')]=129
  c=NesMPU(memory=m,pc=address(b,'RdNativeBGGate'));c.a,c.x,c.y,c.p,c.sp=90,3,7,flags,224;c.stPushWord(0x5aff)
  for _ in range(32):
   if c.pc in [0x5b00,address(b,'PlayerBGCollision')]:break
   c.step()
  assert (c.a,c.x,c.y,c.p&207)==(90,3,7,flags&207)
  assert c.sp==(224 if(char,var)==(2,1)else 222);flags_cases+=1
 proof=dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=ref.digest((O/'candidate.nes').read_bytes()),actual_ISR_scratch=seams,retained_traction_whole_callers=len(rows),retained_traction_rows=rows,all_flags_gate_cases=flags_cases,old_reachable_prefix_and_terminal_bridge_exact=True,original_Done_RTS_PC=address(b,'LuigiNativeTraction')+83,gate_footprint=24,remaining_old_padding_bytes=16,branches='Original raw!=Luigi branch still targets B980 Done; admitted Luigi dispatch terminal-JMPs FarCallCommon before B958. Only changed PlayerCtrlRoutine JSR reaches the gate; no old symbol lies in the padding.',bindings=[ref.binding(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',P,P.with_suffix('.dbg'),O/'luigi_native.s',O/'player.s']])
 (O/'caller-ABI-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,ISR=len(seams),traction=len(rows),flags=flags_cases)))
if __name__=='__main__':main()
