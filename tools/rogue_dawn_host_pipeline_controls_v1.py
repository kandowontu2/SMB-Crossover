"""Real IdleLoop/GameLoop motion callers; private CPU evidence, no native run."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_deferred_controls_v1 as d
import rogue_dawn_map_v1 as ref
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import seed,run,app,registers,cleanwrites,smc_at
O=R/'build/rogue-dawn-host-pipeline-v1';B=O/'candidate.nes';P=R/'build/roster-shared-rcr-adopted-v8.nes'

def base(b,kind='floor',face=0,keys=0,wx=128):
 m=d.old.make(b)
 for n,v in [('OperMode_Task',3),('PlayerEntranceCtrl',2),('GameTimerDisplay',4),('SavedJoypadBits',keys),('ScreenRight_X_Pos',255),('Player_Rel_XPos',96)]:m[address(b,n)]=v
 d.call(m,'RdHsNewSession',sp=240)
 m[address(b,'Player_X_Position')]=(wx-8)&255;m[address(b,'Player_PageLoc')]=(wx-8)//256
 m[0x5c2c]=face
 if kind=='head':
  m[address(b,'Player_Y_Position')]=175;m[0x5c00]=2;m[0x5c08]=253;m[0x5c14]=26;m[0x5c03]=12;m[0x5c05]=m[0x5c06]=12
  for xx in range(max(0,wx-16),min(512,wx+32),16):d.old.tile(m,xx,175,0x60)
 elif kind=='side':
  m[address(b,'Player_Y_Position')]=142;m[0x5c00]=2;m[0x5c08]=4;m[0x5c14]=26
  for yy in [144,160,176,192]:d.old.tile(m,wx+(16 if not face else -16),yy,0x14)
 if kind!='open':
  for xx in range(0,512,16):d.old.tile(m,xx,208,0x61)
 return m

def idle(m,seam=None,public_sp=253,poison=None):
 """Real Reset JSR IdleLoop entryFD -> PHA/JSR GameLoop entryFA.

 This also follows the real one-catch-up path after an injected lag NMI.
 Regular mid-Main NMI is not admitted: GameLoop has set NmiDisableFF.
 """
 b=m.bundle
 if seam:
  d.service.invoke(m,address(b,'AudioInit'),sp=240);d.service.invoke(m,address(b,'SamusAudioInit'),sp=240)
  m[address(b,'AreaMusicQueue')]=1
 c=NesMPU(memory=m,pc=address(b,'IdleLoop'));c.sp=public_sp;c.p=0x71
 low=c.sp;fired=False;points=[];m.writes.clear();seenmain=0;probe=[];track=False;written=set();firstread=[]
 names=['GameLoop','RdTxMovement','RdControlStep','RdTxMovementFlush','RdTxPrepareActor','RdHsPrepareActor','RdNativeBGGate','PlayerBGCollision','NativeRarePlayerHeadCollisionCore']
 targets={(address(b,n),(location(b,n)-16)//8192):n for n in names}
 zp={address(b,'R'+str(i)) for i in range(8)}
 # Track actual loads/stores at the first caller continuation after movement.
 oldclass=m.__class__
 class Scratch(oldclass):
  def __getitem__(self,k):
   if track and isinstance(k,int) and k in zp and k not in written:firstread.append(k)
   return super().__getitem__(k)
  def __setitem__(self,k,v):
   if track and isinstance(k,int) and k in zp:written.add(k)
   return super().__setitem__(k,v)
 m.__class__=Scratch
 for steps in range(500000):
  if c.pc==address(b,'IdleLoop') and steps>0:break
  bank=m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
  key=(c.pc,bank)
  if key in targets:
   n=targets[key];points.append(dict(entry=n,SP=c.sp,physical_A=m.banks[1],physical_C=m.banks[2]))
   if n=='GameLoop':seenmain+=1
   if n=='RdNativeBGGate':track=False
  if c.pc==address(b,'GuestVictoryAfterMovement') and bank==1:
   if poison is not None:
    for i,z in enumerate(sorted(zp)):m[z]=(poison+i*31)&255
   track=True;written.clear()
  if seam and not fired and key==seam[:2]:
   fired=True
   before=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(m.banks),m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],bytes(m[z]for z in smc_at(b)),bytes(m[0x101+c.sp:0x200]),bytes(m[0x5c00:0x5c80]))
   expected=list(m.banks)
   if seam[2]=='IRQ':c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
   else:c.nmi()
   for _ in range(50000):
    low=min(low,c.sp);c.step()
    if c.pc==before[5] and c.sp==before[4]:break
   else:raise AssertionError(('ISR timeout',seam,hex(c.pc)))
   after=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(m.banks),m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],bytes(m[z]for z in smc_at(b)),bytes(m[0x101+c.sp:0x200]),bytes(m[0x5c00:0x5c80]))
   assert after==before,('actual ISR context',seam,before,after)
  assert m[c.pc]!=0,('BRK',hex(c.pc),m.banks,c.sp)
  c.step();low=min(low,c.sp)
 else:raise AssertionError(('IdleLoop update timeout',hex(c.pc),m.banks))
 m.__class__=oldclass
 assert c.sp==public_sp and 1<=seenmain<=2,(c.sp,seenmain)
 assert low>=128,('live stack guard128',low)
 assert not seam or fired,('unreached seam',seam)
 return c,dict(minimum_SP=low,actual_Main_calls=seenmain,entries=points,scratch_read_before_write=sorted(set(firstread)))

def main():
 b=d.old.scoped_load(B);parent=d.old.scoped_load(P);checks={};proof=dict(passed=False,native_run=False,source_CPU_only=True,ROM_sha256=ref.digest(B.read_bytes()),checks=checks)
 try:
  # Literal standalone ABI remains separate and its negative is not relabelled.
  old=d.old.scoped_load(R/'build/rogue-dawn-host-deferred-v1/candidate.nes')
  spans=[]
  for n in ['RdControlStep','RdControlDispatch','RdHostBridgeStart','RdTxAfterMovement']:
   size=int(b['syms'][n]['size'],0) if n!='RdHostBridgeStart' else 175
   pa,pb=location(old,n),location(b,n);assert old['raw'][pa:pa+size]==b['raw'][pb:pb+size]
   spans.append(dict(symbol=n,bytes=size))
  checks['preserved_standalone_negative_and_callback_code']=dict(exact_spans=spans,negative=ref.binding(R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json'),interpretation='Standalone preserved flush fails SP192; frozen callback-only ControlStep is qualified separately at192. No component failure is hidden.')
  # All PAD campaign completed before that recorded standalone failure; its
  # exact compiled control/bridge/deferred source is unchanged in this image.
  source=[]
  for name,bank in [('RdHostCall95',124),('RdHsGeometry',95),('RdTxHead',95),('RdHsDraw',95)]:
   for kind in ['IRQ','lagNMI']:
    m=d.setup(b);d.call(m,'RdTxMovementBegin');c,l,tr=d.call(m,'RdControlStep',seam=(address(b,name),bank,kind))
    assert l>=128;source.append(dict(entry=name,kind=kind,SP=192,minimum_SP=l))
  checks['frozen_ControlStep_192_real_interrupts']=source
  # Every valid native raw identity reaches the old full collision body;
  # exact Rogue returns at the gate, preserving incoming full AXYP/SP.
  rows=[]
  for char,var in itertools.product(range(256),[0,1,2]):
   m=d.old.make(b);m[address(b,'SelectedCharacter')]=char;m[0x5fee]=var
   c=NesMPU(memory=m,pc=address(b,'RdNativeBGGate'));m.page(1,1);m[address(b,'CurrentBank')]=129
   c.a,c.x,c.y,c.p,c.sp=90,3,7,0x71,224;c.stPushWord(0x5aff);start=(c.a,c.x,c.y,c.p&207)
   for k in range(32):
    if c.pc in [0x5b00,address(b,'PlayerBGCollision')]:break
    c.step()
   else:raise AssertionError('Gate timeout')
   assert (c.a,c.x,c.y,c.p&207)==start
   owned=(char,var)==(2,1)
   assert c.pc==(0x5b00 if owned else address(b,'PlayerBGCollision'))
   assert c.sp==(224 if owned else 222)
   rows.append(c.processorCycles)
  checks['exact_24B_BG_gate']=dict(cases=len(rows),gate_PC=address(b,'RdNativeBGGate'),foreign_added_CPU=sorted(set(rows)-{rows[2*3+1]}),Rogue_CPU=rows[7],original_player_BG_not_called_for_Rogue=True)
  # Whole foreign active GameLoops, including real Luigi movement, preserve
  # all application state/CPU returns/ordered nonbank bus writes. CPU cost is
  # deliberately measured, never masked into a claim of zero added work.
  profiles=[(0,'MarioVariant',0),(0,'MarioVariant',1),(0,'MarioVariant',4),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,'RdVariant',0),(3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),(6,None,0),(7,None,0),(9,'RlVariant',0),(9,'RlVariant',1),(10,None,0),(11,None,0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,None,0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),(19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,None,0)]
  foreign=[]
  for (char,key,var),mode in itertools.product(profiles,[0,1]):
   pair=[]
   for bundle in [parent,b]:
    q=seed(bundle,char)
    if key=='RdVariant':q.m[0x5fee]=var # approved selector is unlinked in parent4cbd
    elif key:q.set(key,var)
    q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
    c,w,_=run(q,'GameLoop',p=0x71);pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
   assert pair[0][:4]==pair[1][:4],('foreign complete GameLoop',char,key,var,mode,pair[0][0],pair[1][0])
   foreign.append(dict(raw=char,variant=var,mode=mode,CPU_delta=pair[1][4]-pair[0][4]))
  checks['all_foreign_complete_GameLoop']=foreign
  # All real admission paths normal/catch-up use the literal IdleLoop caller;
  # current active controller admits only engine8 and Player_State!=3.
  whole=[]
  for kind,face,keys,wx in itertools.product(['open','floor','head','side'],[0,1],[0,1,128,129],[128,252,260]):
   m=base(b,kind,face,keys,wx);c,row=idle(m)
   assert any(r['entry']=='RdControlStep' for r in row['entries'])
   assert not any(r['entry']=='PlayerBGCollision' for r in row['entries'])
   assert m[0x5c0b]==255 and m[0x5c3b]==0
   assert not row['scratch_read_before_write'],row
   row.update(kind=kind,facing=face,keys=keys,worldX=wx);whole.append(row)
  checks['actual_IdleLoop_complete_Main_movement_callers']=whole
  seams=[]
  for name,bank,kind0 in [('RdTxMovement',95,'head'),('RdControlStep',124,'head'),('RdTxHead',95,'head'),('RdTxMovementFlush',95,'head'),('NativeRarePlayerHeadCollisionCore',9,'head'),('SetupPowerUp',126,'head'),('NrPrepare',124,'head'),('RdNrPrepare',124,'head'),('RdTxPrepareActor',95,'head'),('RdHsPrepareActor',95,'head'),('RdNativeBGGate',1,'floor')]:
   for interrupt in ['IRQ','lagNMI']:
    m=base(b,kind0,0,128);c,row=idle(m,seam=(address(b,name),bank,interrupt));row.update(entry=name,interrupt=interrupt);seams.append(row)
  checks['actual_Main_IRQ_lag_seams']=seams
  proof.update(passed=True,host_layout=dict(start=0xa600,deferred_component_end=address(b,'RdTxEnd'),actual_end=address(b,'RdTxMovementEnd'),actual_bytes=address(b,'RdTxMovementEnd')-0xa600),limitations=['Only motion/BG transaction integration is installed privately. Legacy graphics/actor hurt/item-contact/audio/menu/lifecycle hooks are NOT admitted as complete Rogue gameplay. Complete Main execution here establishes actual call/stack provenance in typed source arenas, not native graphics/game correctness.','Standalone preserved flush192 negative remains. Movement-only flush has no incoming R0..7 preservation contract; actual post-movement caller liveness is checked instruction-by-instruction.','No native Mesen run, deadline/FPS/PPU/audio/all-room claim.'])
 except BaseException as e:
  proof.update(error=str(e),traceback=traceback.format_exc());raise
 finally:
  proof['bindings']=[ref.binding(p)for p in[Path(__file__),B,B.with_suffix('.dbg'),O/'build.json',R/'src/rogue_dawn_host_pipeline.s',O/'movement-flush.s',R/'src/rogue_dawn_host_deferred.s',R/'tools/rogue_dawn_host_deferred_negative_v1.py',R/'tools/audit/sunny_integrated_controls_v1.py',P]]
  (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,foreign=len(foreign),Main=len(whole),ISR=len(seams),minimum_SP=min(r['minimum_SP']for r in whole+seams))))
if __name__=='__main__':main()
