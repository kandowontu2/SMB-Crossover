"""Actual foreign callers and initialized interrupt seams for private lifecycle.

CPU source qualification only. No emulated gameplay/capture or native claim.
"""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_lifecycle_controls_v1 as c
from check_tmnt_render_oa import address,location
from sunny_integrated_controls_v1 import seed,run,app,registers,cleanwrites
O=c.O
PROFILES=[(0,'MarioVariant',0),(0,'MarioVariant',1),(0,'MarioVariant',4),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,None,0),(3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),(6,None,0),(7,None,0),(9,'RlVariant',0),(9,'RlVariant',1),(10,None,0),(11,None,0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,None,0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),(19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,None,0)]

def foreign(bundle,char,key,var,mode=1):
 q=seed(bundle,char)
 if key:q.set(key,var)
 q.m[0x5fee]=0
 q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
 return q

def main():
 b=c.d.old.scoped_load(O/'candidate.nes');old=c.d.old.scoped_load(c.P);checks={};minimum=255
 proof=dict(passed=False,source_CPU_only=True,native_run=False,ROM_sha256=c.ref.digest((O/'candidate.nes').read_bytes()),checks=checks)
 try:
  rows=[]
  for(char,key,var),mode in itertools.product(PROFILES,[0,1]):
   pair=[]
   for bundle in[old,b]:
    q=foreign(bundle,char,key,var,mode);cpu,w,_=run(q,'GameLoop',p=0x71)
    pair.append((registers(cpu),app(q),tuple(q.m.banks),cleanwrites(q,w),cpu.processorCycles))
   assert pair[0][:4]==pair[1][:4],('foreign Main',char,key,var,mode,pair[0][0],pair[1][0])
   rows.append(dict(raw=char,variant=var,mode=mode,CPU_delta=pair[1][4]-pair[0][4]))
  checks['all_foreign_full_Main_application_ordered_writes_AXYP_banks']=rows
  rows=[]
  # Actual public callers start/return in the same physical bank; the new
  # A95 wrapper cannot hide its incoming-register or physical-C effects.
  for(char,key,var),name,p in itertools.product(PROFILES,['GuestPlayerVisible','GuestInjuryStatus','GuestBodyContactBridge','InjurePlayer','PlayerDeath','NrFreshGameInit'],c.body.FLAGS[:2]):
   pair=[]
   for bundle in[old,b]:
    q=foreign(bundle,char,key,var);q.put(ObjectOffset=0)
    cpu,w,_=run(q,name,a=91,x=0,y=7,p=p)
    pair.append((registers(cpu),app(q),tuple(q.m.banks),cleanwrites(q,w),cpu.processorCycles))
   assert pair[0][:4]==pair[1][:4],('foreign public',char,key,var,name,p,pair[0][0],pair[1][0])
   rows.append(dict(raw=char,variant=var,caller=name,P=p,CPU_delta=pair[1][4]-pair[0][4]))
  checks['foreign_real_public_return_callers']=rows
  rows=[]
  # The new callback's sole admitted addition is death35. Every old real
  # source pose retains actual returnAXYP, radius, context-X, pointer, C94
  # lease and applicationRAM, including the declared F7 empty form.
  for frame,face,p in itertools.product(sorted(c.art.BODY)+[247],[0,1],c.body.FLAGS):
   pair=[]
   for bundle in[old,b]:
    m=c.make(bundle);m[0x5c03]=frame;m[0x5c2c]=face
    cpu,low,trace=c.d.call(m,'RdHostDrawPlayer',a=91,x=4,y=7,p=p,sp=224)
    pair.append(c.body.snapshot(m,cpu)+(cpu.processorCycles,))
   assert pair[0][:3]==pair[1][:3],('old genuine source draw callback',frame,face,p)
   rows.append(dict(frame=frame,facing=face,P=p,CPU_delta=pair[1][3]-pair[0][3]))
  checks['all_old_source_draw_callback_returns_and_context_exact']=rows
  rows=[]
  # The exact-owner check must precede ANY source-overlay read even on
  # invalid selectors. Test only the new private entries, not inherited
  # foreign engines which legitimately own this shared identity overlay.
  names=['RdLifeUi','RdLifeGameRoutines','RdLifeCheatRoutines','RdLifeFresh','RdLifeArea','RdLifeMovement','RdLifeVisible','RdLifeStatus','RdLifeInjury','RdLifeBody','RdLifeDeathStart','RdLifeDeathTick','RdLifeDraw','RdLifeGraphics','RdLifeDynamicPrg']
  # Direct no-owner returns through real fallback engines can read their own
  # overlays; watch only until the genuine foreign target entry, not its body.
  targets={'RdLifeUi':'X5BounceUiDispatch','RdLifeGameRoutines':'GameRoutines','RdLifeCheatRoutines':'CheatsGameRoutinesGate','RdLifeFresh':'CmHostFresh','RdLifeArea':'Z2ResetAreaGate','RdLifeMovement':'RdTxMovement','RdLifeVisible':'RlVisibleDispatch','RdLifeStatus':'RlInjuryStatusDispatch','RdLifeInjury':'RlInjuryDispatch','RdLifeBody':'LmBodyGate','RdLifeDeathStart':'Cv3FxDeathDispatch','RdLifeDeathTick':'SamusDeathUpdate','RdLifeGraphics':'RdBodyGraphics','RdLifeDynamicPrg':'RdBodyDynamicPrg'}
  from verify_native_relocation import NesMPU
  for char,var,name in itertools.product([0,1,2,21,23,255],[0,1,2,255],names):
   if(char,var)==(2,1):continue
   m=c.make(b);c.put(m,SelectedCharacter=char);m[0x5fee]=var;m.page(1,95);m[address(b,'CurrentBank')]=223
   cpu=NesMPU(memory=m,pc=address(b,name));cpu.sp=224;cpu.a,cpu.x,cpu.y,cpu.p=91,4,7,0x71;cpu.stPushWord(0x5aff);m.reads.clear();m.writes.clear()
   for _ in range(250):
    if cpu.pc==0x5b00 or(name in targets and cpu.pc==address(b,targets[name])and m.banks[1]==(location(b,targets[name])-16)//8192):break
    cpu.step()
   else:raise AssertionError(('foreign owner-gate timeout',char,var,name))
   owned=set(range(0x5c00,0x5c80))|set(range(0x5fb0,0x5fb8))
   assert not m.reads&owned and not any(a in owned for a,v in m.writes),(char,var,name)
   rows.append(dict(raw=char,variant=var,entry=name,source_overlay_accesses=0))
  checks['exact_ID_before_any_Rogue_overlay_access']=rows
  rows=[]
  for name,kind,fixed in itertools.product(['RdLifeUi','RdLifeGameRoutines','RdLifePrepareMain','RdLifeMovement','RdLifeDraw','RdLifeVisible','RdLifeGraphics','RdLifeDynamicPrg'],['IRQ','lagNMI'],[125,127]):
   m=c.make(b);m.page(3,fixed)
   cpu,row=c.mainstep(m,first=True,seam=(address(b,name),95,kind));minimum=min(minimum,row['minimum_SP'])
   rows.append(dict(entry=name,interrupt=kind,fixed_bank=fixed,**row))
  checks['actual_Main_new_owner_IRQ_lag_both_fixed_copies']=rows
  rows=[]
  # Interrupts across every instruction that writes the new visibility
  # target's genuine5SMC setup. In particular, partial target-low/high state
  # must be restored before the interrupted instruction resumes.
  build=json.loads((O/'build.json').read_text())
  span=next(x for x in build['old_hook_spans']if x['name']=='GuestPlayerVisible->RlVisibleDispatch')
  start=address(b,'GuestPlayerVisible')+span['start']-location(b,'GuestPlayerVisible')
  hookbank=(span['start']-16)//8192
  for offset,kind,fixed in itertools.product([0,3,5,8,10,13,15],['IRQ','lagNMI'],[125,127]):
   m=c.make(b);m.page(3,fixed)
   cpu,row=c.mainstep(m,first=True,seam=(start+offset,hookbank,kind));minimum=min(minimum,row['minimum_SP'])
   rows.append(dict(actual_PC=hex(start+offset),offset=offset,interrupt=kind,fixed_bank=fixed,**row))
  checks['actual_visibility_farcall_all_SMC_instruction_seams']=rows
  rows=[]
  for name,kind in itertools.product(['RdLifeStatus','RdLifeInjury','RdHsDamage','RdLifeBeginDeath','RdLifeDeathStart'],['IRQ','lagNMI']):
   m=c.make(b);m[0x5fb4:0x5fb6]=bytes([0x10,0]);c.target(m)
   cpu,low,trace=c.d.call(m,'InjurePlayer',sp=224,seam=(address(b,name),95,kind));minimum=min(minimum,low)
   assert c.get(m,'GameEngineSubroutine')==11 and m[0x5c00]==7
   rows.append(dict(entry=name,interrupt=kind,minimum_SP=low))
  for name,kind in itertools.product(['RdLifeDeathTick','RdLifeDraw','RdLifeDeathMetadata'],['IRQ','lagNMI']):
   m=c.make(b);m[0x5fb4:0x5fb6]=bytes([0x10,0]);c.target(m);c.d.call(m,'InjurePlayer',sp=224)
   cpu,low,trace=c.d.call(m,'PlayerDeath',sp=224,seam=(address(b,name),95,kind));minimum=min(minimum,low)
   assert m[0x5c03]==53
   rows.append(dict(entry=name,interrupt=kind,minimum_SP=low))
  for name,kind in itertools.product(['RdLifeArea','RdBodyNewLife','RdHsNewLife'],['IRQ','lagNMI']):
   m=c.make(b);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x12,0x19]);c.put(m,MmDeathFlag=1)
   cpu,low,trace=c.d.call(m,'RdLifeArea',sp=224,seam=(address(b,name),95,kind));minimum=min(minimum,low)
   assert list(m[0x5fb0:0x5fb6])==[255,7,15,3,0x99,0x39]
   rows.append(dict(entry=name,interrupt=kind,minimum_SP=low))
  checks['real_contact_death_life_IRQ_lag_seams']=rows
  proof.update(passed=True,minimum_SP=minimum,limits=['Source CPU controls only; no native/PPU/audio/deadline/playable claim.','Existing two Proto lag/catch-up fixture FALSEs remain bound in immutable body-edge-controls.json; no blanket foreign lag coverage.','Direct-call entrySP224 used for injury/reset protocols; full Main uses genuine IdleLoopSP253 and source ControlStep natural admission.'])
 except BaseException as e:proof.update(error=str(e),traceback=traceback.format_exc());raise
 finally:
  proof['bindings']=[c.ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_host_lifecycle_controls_v1.py',O/'candidate.nes',O/'candidate.dbg',O/'build.json',c.P,c.P.with_suffix('.dbg'),c.body.O/'body-edge-controls.json']]
  (O/'edge-controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,minimum_SP=minimum,counts={k:len(v)for k,v in checks.items()})))
if __name__=='__main__':main()
