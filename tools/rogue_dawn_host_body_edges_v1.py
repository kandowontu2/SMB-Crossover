"""Additional genuine ABI/SMC/platform seams and foreign world fast path."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_body_controls_v1 as c
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import seed,run,registers,app,cleanwrites
O=c.O

def main():
 b=c.d.old.scoped_load(O/'candidate.nes');old=c.d.old.scoped_load(c.P);checks={};minimum=255
 # Every instruction boundary of the15B selector trampoline, including the
 # partially written real SMC target word; actual complete Main caller.
 rows=[]
 for offset,kind in itertools.product([0,2,5,7,10,12],['IRQ','lagNMI']):
  m=c.pipe.base(b);c.vis(m)
  cpu,row=c.pipe.idle(m,seam=(address(b,'RdBodyBoxSelectBridge')+offset,1,kind));minimum=min(minimum,row['minimum_SP'])
  rows.append(dict(offset=offset,interrupt=kind,**row))
 checks['all_selector_instruction_SMC_seams']=rows
 # Real horizontal carry is committed before callback. Inject at the actual
 # new owned landing and box consumers; no fake return/trampoline target.
 rows=[]
 for ry,name,kind in itertools.product([8,15],['RdBodyPositionPlatform','RdBodyBoxOwn'],['IRQ','lagNMI']):
  m=c.pipe.base(b);m[0x5c01]=ry
  c.put(m,Player_X_Position=255,Player_PageLoc=0)
  m[address(b,'Enemy_Y_Position')]=176;m[address(b,'Enemy_Y_HighPos')]=1;m[address(b,'Enemy_ID')]=40;m[address(b,'R0')]=1
  cpu,low,trace=c.d.call(m,'PositionPlayerOnHPlat',a=176,x=0,sp=224,seam=(address(b,name),95,kind));minimum=min(minimum,low)
  assert c.get(m,'Player_PageLoc')==1 and c.get(m,'Player_X_Position')==0
  assert c.bbox(m)==c.expectbox(m)and c.get(m,'Player_Y_Position')==176-ry-17
  rows.append(dict(radiusY=ry,entry=name,interrupt=kind,minimum_SP=low,final_page=1,final_X=0))
 checks['actual_platform_carry_IRQ_lag_seams']=rows
 # Genuine world helperRAM descriptors keep the original world CPY/BNE/JMP
 # path before any A95 call. Every physicalC input yields the same result.
 rows=[]
 for slot,physicalC,p in itertools.product([1,6],[0,12,33,65,94],[0x30,0x31,0x70,0x71]):
  pair=[]
  for bundle in[old,b]:
   m=c.d.old.make(bundle);m.page(1,4);m.page(2,physicalC);m[address(bundle,'CurrentBank')]=132;m[address(bundle,'CurrentBankC')]=physicalC|128
   cpu=NesMPU(memory=m,pc=address(bundle,'MmDynamicPlayerPrgOwner'));cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=91,4,slot,p,224
   initial=(cpu.a,cpu.x,cpu.y,cpu.p&76,tuple(m.banks));m.writes.clear()
   for _ in range(8):
    if cpu.pc==address(bundle,'HpNativePointerEnd'):break
    cpu.step()
   else:raise AssertionError('world fast path')
   assert(cpu.a,cpu.x,cpu.y,cpu.p&76,tuple(m.banks))==initial
   assert not m.writes,'world path must not touch SMC/banks'
   pair.append((cpu.pc,cpu.processorCycles,cpu.p,tuple(m.banks)))
  assert pair[0]==pair[1]
  rows.append(dict(slot=slot,physicalC=physicalC,P=p,CPU=pair[1][1],writes=0))
 checks['all_world_fast_path_before_farcall']=rows
 # Actual foreign platform callers compare full returned AXYP/SP/banks and
 # applicationRAM, all forms/carry/page edge. Old native owner stays intact.
 rows=[]
 for char,var,owner,slot,top,delta in itertools.product([0,1,2,4,15,21,23],[0,1],['PositionPlayerOnHPlat','PositionPlayerOnVPlat','PositionPlayerOnS_Plat'],[0,4],[64,176],[0,1,255]):
  if(char,var)==(2,1)or(owner=='PositionPlayerOnS_Plat'and delta):continue
  pair=[]
  for bundle in[old,b]:
   m=c.d.old.make(bundle);c.put(m,SelectedCharacter=char,Player_X_Position=255);m[0x5fee]=var
   m[address(bundle,'Enemy_Y_Position')+slot]=top;m[address(bundle,'Enemy_Y_HighPos')+slot]=1;m[address(bundle,'Enemy_ID')+slot]=40;m[address(bundle,'R0')]=delta
   cpu,low,trace=c.d.call(m,owner,a=2 if owner=='PositionPlayerOnS_Plat'else top,x=slot,p=0x71,sp=224)
   pair.append(c.snapshot(m,cpu)+(cpu.processorCycles,))
  assert pair[0][:3]==pair[1][:3],(char,var,owner,slot,top,delta)
  rows.append(dict(raw=char,variant=var,owner=owner,slot=slot,top=top,delta=delta,CPU_delta=pair[1][3]-pair[0][3]))
 checks['foreign_complete_platform_callers']=rows
 # Foreign fullMain interrupts pass through the new exact-owner gates while
 # retaining their real native controller/draw owners. Context is snapshotted
 # at actual PC/SP, including fiveSMC and the active guest overlay.
 rows=[]
 for(char,key,var),gate,kind in itertools.product([(0,'MarioVariant',0),(0,'MarioVariant',4),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,None,0),(21,'RcVariant',1)],['RdBodySelectBox','RdBodyBox'],['IRQ']):
  q=seed(b,char)
  q.m.__class__=c.d.service.TracedMemory;q.m.reads=set()
  # Real reset's complete guest initializer, not an audio-zeroed arena.
  run(q,'CrossoverInit');q.set('SelectedCharacter',char)
  if key:q.set(key,var)
  q.m[0x5fee]=0;q.put(GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
  c.d.service.invoke(q.m,address(b,'MegaManAudioInit'),sp=240)
  try:cpu,row=c.pipe.idle(q.m,seam=(address(b,gate),95,kind))
  except Exception as e:raise AssertionError((char,key,var,gate,kind,str(e)))from e
  minimum=min(minimum,row['minimum_SP'])
  rows.append(dict(raw=char,variant=var,entry=gate,interrupt=kind,**row))
 checks['foreign_actual_Main_IRQ_new_gates']=rows
 # A separate broader foreign Proto catch-up fixture is NOT qualified. Its
 # same literal failure is retained on old e4b788 and new f1ed39, after the
 # injected real ISR context check passed. No shared engine cause inferred.
 negatives=[]
 for path,gate,bank in[(R/'build/rogue-dawn-host-pipeline-v2/candidate.nes','MegaManCollisionBox',126),(O/'candidate.nes','RdBodySelectBox',95)]:
  z=c.d.old.scoped_load(path);q=seed(z,1);q.m.__class__=c.d.service.TracedMemory;q.m.reads=set();run(q,'CrossoverInit');q.set('SelectedCharacter',1);q.set('ProtoVariant',1);q.m[0x5fee]=0;q.put(GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1);c.d.service.invoke(q.m,address(z,'MegaManAudioInit'),sp=240)
  try:c.pipe.idle(q.m,seam=(address(z,gate),bank,'lagNMI'))
  except AssertionError as e:negatives.append(dict(ROM=ref.binding(path),gate=gate,error=str(e),status='FALSE retained; outside this bounded body unit; cause unresolved'))
  else:raise AssertionError('Expected retained countercheck changed')
 assert negatives[0]['error']==negatives[1]['error']=="('BRK', '0xbb1a', [126, 0, 65, 127], 241)"
 checks['foreign_Proto_catchup_unqualified_baseline_countercheck']=dict(negative_rows=negatives,scope='Not a native failure, not accepted as a shared engine/audio defect. No blanket foreign lag/catch-up qualification. This extra typed fixture is unchanged-negative on both hashes; original foreign fullMain/draw and actual IRQ comparisons remain separately measured.')
 proof=dict(passed=True,native_run=False,source_CPU_only=True,qualification='Bounded body unit only; separate foreign Proto catch-up fixture remains FALSE/unqualified.',ROM_sha256=ref.digest((O/'candidate.nes').read_bytes()),minimum_SP=minimum,checks=checks,bindings=[ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_host_body_controls_v1.py',O/'candidate.nes',O/'candidate.dbg',c.P,c.P.with_suffix('.dbg')]])
 (O/'body-edge-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,minimum_SP=minimum,counts={k:len(v)for k,v in checks.items()})))
if __name__=='__main__':main()
