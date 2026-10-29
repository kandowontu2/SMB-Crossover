"""Actual caller lifecycle/contact/visibility CPU controls, not native proof."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_body_controls_v1 as body
import rogue_dawn_map_v1 as ref
import prepare_rogue_dawn_art_v1 as art
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import seed,run,app,registers,cleanwrites,smc_at
O=R/'build/rogue-dawn-host-lifecycle-v1';P=body.O/'candidate.nes';d=body.d
get,put=body.get,body.put

def make(b,mode=1):
 m=body.pipe.base(b);put(m,CrossoverBehaviorVersion=mode)
 # Real original source audio initializers. Audio playback remains OPEN;
 # these prevent the preserved zero-bank pseudo-driver fixture mistake.
 for name in ['AudioInit','MegaManAudioInit','SamusAudioInit']:d.service.invoke(m,address(b,name),sp=240)
 return m

def wake(m):
 """Actual regular NMI admission between complete Mains, not a fake clock."""
 b=m.bundle;c=NesMPU(memory=m,pc=0x5b00);c.sp=253;c.p=0x71
 old=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],bytes(m[z]for z in smc_at(b)))
 c.nmi();low=255
 for _ in range(100000):
  low=min(low,c.sp)
  if c.pc==old[0]and c.sp==old[5]:break
  assert m[c.pc]!=0,('NMI BRK',hex(c.pc),m.banks)
  c.step()
 else:raise AssertionError('NMI timeout')
 now=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks),m[address(b,'CurrentBank')],m[address(b,'CurrentBankC')],bytes(m[z]for z in smc_at(b)))
 assert now==old,('real regular NMI context',old,now)
 assert get(m,'NmiDisable')!=0
 return low

def mainstep(m,first=False,seam=None):
 if not first:wake(m)
 c,row=body.pipe.idle(m,seam=seam);return c,row

def target(m,ident=6,side=1):
 b=m.bundle;put(m,ObjectOffset=0)
 for n,v in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_PageLoc',get(m,'Player_PageLoc')),('Enemy_X_Position',(get(m,'Player_X_Position')+side*8)&255),('Enemy_Y_Position',get(m,'Player_Y_Position')),('Enemy_Y_HighPos',1),('Enemy_BoundBoxCtrl',9),('EnemyOffscrBitsMasked',0)]:m[address(b,n)]=v

def main():
 b=d.old.scoped_load(O/'candidate.nes');parent=d.old.scoped_load(P);checks={};proof=dict(passed=False,source_CPU_only=True,native_run=False,ROM_sha256=ref.digest((O/'candidate.nes').read_bytes()),checks=checks);minimum=255
 try:
  # Actual InitializeArea target and real full reset chain preserve resources
  # across scenes/refill life, independent of futurepipe AreaPointer.
  rows=[]
  for dead,health,gear,mode in itertools.product([0,1],[(0x12,0x19),(0,0)],[0,255],[0,1]):
   m=make(b,mode);m[0x5fb0:0x5fb6]=bytes([gear,7,15,3,*health]);put(m,MmDeathFlag=dead,AreaPointer=0xc2,AreaType=1,AreaAddrsLOffset=5,SavedJoypadBits=128)
   # Real private target called by native InitializeArea before native clear.
   c,low,tr=d.call(m,'RdLifeArea',sp=224);minimum=min(minimum,low)
   expected=[gear,7,15,3,0x99,0x39]if dead or health==(0,0)else[gear,7,15,3,*health]
   assert list(m[0x5fb0:0x5fb6])==expected
   assert m[0x5c00]==0 and m[0x5c0b]==255 and m[0x5c3b]==0 and m[0x5c7c]==1
   assert get(m,'GuestHurtKind')==get(m,'GuestHurtTicks')==get(m,'GuestPowerupActive')==0
   assert any(pc==address(b,'MegaManResetArea')and bank==10 for pc,bank in tr)
   rows.append(dict(death_receipt=dead,initial_health=list(health),gear=gear,mode=mode,persistent_after=expected,minimum_SP=low,CPU=c.processorCycles))
  checks['actual_area_target_genuine_clear_then_source_init']=rows
  rows=[]
  for dead,mode in itertools.product([0,1],[0,1]):
   m=make(b,mode);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x12,0x19]);put(m,MmDeathFlag=dead,AreaPointer=0x25,AreaType=1,AreaAddrsLOffset=5)
   cpu,low,trace=d.call(m,'InitializeArea',sp=240);minimum=min(minimum,low)
   expected=[255,7,15,3,0x99,0x39]if dead else[255,7,15,3,0x12,0x19]
   assert list(m[0x5fb0:0x5fb6])==expected and list(m[0x5c00:0x5c04])==[0,15,4,8]
   assert any(pc==address(b,'RdLifeArea')and bank==95 for pc,bank in trace)
   rows.append(dict(death_receipt=dead,mode=mode,minimum_SP=low,persistent_after=expected,native_initialize_after_wrapper=True))
  checks['complete_native_InitializeArea_after_source_reset']=rows
  rows=[]
  for dead,mode in itertools.product([0,1],[0,1]):
   m=make(b,mode);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x12,0x19]);put(m,OperMode_Task=0,MmDeathFlag=dead,AreaPointer=0x25,AreaType=1,AreaAddrsLOffset=5)
   cpu,row=mainstep(m,first=True);minimum=min(minimum,row['minimum_SP'])
   expected=[255,7,15,3,0x99,0x39]if dead else[255,7,15,3,0x12,0x19]
   assert list(m[0x5fb0:0x5fb6])==expected and get(m,'OperMode_Task')==1
   rows.append(dict(death_receipt=dead,mode=mode,minimum_SP=row['minimum_SP'],persistent_after=expected,actual_IdleLoop_Main_initial_area=True))
  checks['genuine_IdleLoop_Main_initial_area_caller']=rows
  # Genuine fresh owner last-child, not a direct invented resource reset.
  rows=[]
  for mode in [0,1]:
   m=make(b,mode);m[0x5fb0:0x5fb6]=bytes([255,17,21,6,0x20,0x29]);put(m,MmDeathFlag=1)
   c,low,tr=d.call(m,'NrFreshGameInit',sp=224);minimum=min(minimum,low)
   assert list(m[0x5fb0:0x5fb6])==[0,0,0,0,0x99,9]
   assert any(pc==address(b,'RdLifeFresh')and bank==95 for pc,bank in tr)
   rows.append(dict(mode=mode,minimum_SP=low,CPU=c.processorCycles))
  checks['real_freshgame_owner']=rows
  # Actual inherited native aliases can be nonzero BEFORE Main. Both real
  # GameRoutinesBridge paths reach source controls rather than legacy hurt.
  rows=[]
  for kind,ticks,injury,power,dead,mode in itertools.product([0,2,3],[0,15],[0,255],[0,1],[0,1],[0,1]):
   m=make(b,mode);put(m,GuestHurtKind=kind,GuestHurtTicks=ticks,InjuryTimer=injury,GuestPowerupActive=power,MmDeathFlag=dead,TimerControl=255,SavedJoypadBits=129)
   # Stale native selected weapon must not run its UI against sourceoverlay.
   m[address(b,'InvSelected')+2]=4
   c,row=mainstep(m,first=True);minimum=min(minimum,row['minimum_SP'])
   assert any(x['entry']=='RdControlStep'for x in row['entries'])
   assert get(m,'GuestHurtKind')==get(m,'GuestHurtTicks')==get(m,'InjuryTimer')==get(m,'GuestPowerupActive')==get(m,'MmDeathFlag')==get(m,'TimerControl')==0
   assert m[0x5c00]==2 and m[0x5c08]&128 and m[0x5c29]==129
   rows.append(dict(old_kind=kind,old_ticks=ticks,old_injury=injury,old_powerup=power,old_deathflag=dead,mode=mode,minimum_SP=row['minimum_SP']))
  checks['complete_Main_no_old_hurt_zero_precondition']=rows
  # Actual source visibility ignores every old injury alias; sourceF7 is
  # hidden and valid source poses shown, including authenticated death35.
  rows=[]
  for frame,old,p in itertools.product([8,27,53,247],[0,1,255],body.FLAGS):
   m=make(b);m[0x5c03]=frame;put(m,GuestHurtKind=old,GuestHurtVisible=old,InjuryTimer=old,MmDeathFlag=old)
   c,low,tr=d.call(m,'GuestPlayerVisible',a=91,x=4,y=7,p=p,sp=224)
   assert bool(c.p&1)==(frame!=247)
   rows.append(dict(frame=frame,old_aliases=old,P=p,visible=bool(c.p&1),CPU=c.processorCycles))
  checks['genuine_visibility_owner_no_old_alias_reads']=rows
  # Actual InjurePlayer/ForceInjury/status/debit caller on each declared
  # actor class; no seed of health/damage OUTCOME, only explicit initial HP.
  eligible=[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,17,18,20,51];rows=[]
  for ident,suit,mode,side in itertools.product(eligible,[0,32],[0,1],[-1,1]):
   m=make(b,mode);m[0x5fb0]=suit;target(m,ident,side);before=bytes(m[0x5fb0:0x5fb4]);put(m,InjuryTimer=0)
   c,low,tr=d.call(m,'InjurePlayer',sp=224);minimum=min(minimum,low)
   # Native low BCD image includes one fractional digit:99HP=09:99;
   # source8HP debit ->09:19, Suit halves to4HP ->09:59.
   expected=[0x59,9]if suit else[0x19,9]
   assert list(m[0x5fb4:0x5fb6])==expected,(ident,suit,mode,side,list(m[0x5fb4:0x5fb6]))
   assert bytes(m[0x5fb0:0x5fb4])==before and m[0x5c0a]==(0x28 if side<0 else 0x20)and m[0x5c1e]==128
   assert get(m,'GameEngineSubroutine')==8 and get(m,'PlayerStatus')==0
   # A second real contact in the same source update cannot pay again.
   d.call(m,'InjurePlayer',sp=224);assert list(m[0x5fb4:0x5fb6])==expected
   rows.append(dict(actor=ident,suit=suit,mode=mode,attacker_side=side,health_after=expected,minimum_SP=low,CPU=c.processorCycles))
  checks['native_contact_status_source_BCD_and_pending_refusal']=rows
  # Genuine full GameLoop collision, rather than merely invoking its injury
  # leaf. Native enemy dispatch first updates a legally staged live Goomba,
  # calculates contact, then actually reaches the new injury owner at SP238.
  rows=[]
  for face,side,suit,mode in itertools.product([0,1],[-1,1],[0,32],[0,1]):
   m=make(b,mode);m[0x5c2c]=face;m[0x5fb0]=suit;target(m,6,side)
   oldstep=NesMPU.step;entries=[]
   def step(cpu):
    if cpu.pc==address(b,'RdLifeInjury')and m.banks[1]==95:entries.append(cpu.sp)
    oldstep(cpu)
   NesMPU.step=step
   try:cpu,row=mainstep(m,first=True)
   finally:NesMPU.step=oldstep
   minimum=min(minimum,row['minimum_SP']);assert entries==[238]
   assert list(m[0x5fb4:0x5fb6])==([0x59,9]if suit else[0x19,9])
   assert m[0x5c0a]==(0x28 if side<0 else 0x20)
   rows.append(dict(facing=face,attacker_side=side,suit=suit,mode=mode,naturally_reached_injury_SP=entries[0],minimum_SP=row['minimum_SP']))
  checks['actual_full_Main_enemy_contact_injury_admission']=rows
  # Complete continuous actual Main/NMI hurt flash chain: hidden/visible
  # frames, native body OAM and original50-count source clock all witnessed.
  rows=[]
  for face,side in itertools.product([0,1],[-1,1]):
   m=make(b);m[0x5c2c]=face;target(m,6,side)
   mainstep(m,first=True)
   # Remove the isolated target AFTER paid contact to inspect source recovery;
   # no health restoration/invulnerability/pose outcome is written.
   m[address(b,'Enemy_Flag')]=0
   previous=None;seen=[]
   for age in range(55):
    c,row=mainstep(m);minimum=min(minimum,row['minimum_SP'])
    clock=m[0x5c1c];frame=m[0x5c03];visible=bool(get(m,'ObjectMetasprite'))
    if previous is not None:assert clock==max(0,previous-1)
    assert visible==(frame!=247)
    assert get(m,'GuestHurtKind')==get(m,'InjuryTimer')==0
    seen.append((clock,frame,visible));previous=clock
   assert seen[0][0]==49 and seen[49][0]==0 and any(not v for _,_,v in seen)and any(v for _,_,v in seen)
   rows.append(dict(facing=face,attacker_side=side,actual_Main_updates=55,clock_frame_visible=seen))
  checks['actual_Main_NMI_50tick_source_hurt_visibility']=rows
  # Authenticated death actual callback before Control resumes: C94bridge
  # remains leased; both distinct C95 records andX24/radii0 are published.
  rows=[];raw=ref.ROM.read_bytes()
  for face,p in itertools.product([0,1],body.FLAGS):
   m=make(b);m[0x5c2c]=face;m[0x5c03]=53
   beforeC=m.banks[2];c,low,tr=d.call(m,'RdHostDrawPlayer',sp=224,p=p)
   assert m.banks[2]==beforeC==94 and m[0x5c01]==m[0x5c02]==0 and c.x==24 and c.y==12
   ptr=get(m,'SmPosePtr')+256*get(m,'SmPosePtr',1);assert ptr==(0xdf19 if face else 0xdf00)
   assert get(m,'SmChrBank')==177
   # Actual graphics target and FIRST record consumer, not mutable endFrame.
   put(m,Player_Y_Position=144,Player_X_Position=120,PlayerFacingDir=face+1,Player_SprAttrib=0,CurrentOAMOffset=0)
   d.call(m,'PlayerGfxHandler',sp=240)
   d.call(m,'HpGraphicsBankCopy',sp=240)
   d.call(m,'DrawMetasprite',sp=240,x=get(m,'ObjectMetasprite'),y=0)
   assert m.banks[2]==95 and get(m,'CurrentCHRBank')==177
   rec_at=16+95*8192+ptr-0xc000;rec=b['raw'][rec_at:rec_at+25];sourceparts,*_=art.native_render(raw,53,face)
   # Source pixel recipe/root proof was independently frozen; bind exact
   # descriptor/CHR here and check all actual emitted part bytes.
   oam=bytes(m[address(b,'Sprite_Data'):address(b,'Sprite_Data')+256])
   for i in range(1,25,4):
    t,a,y,x=rec[i:i+4];x=x-256 if x&128 else x;y=y-256 if y&128 else y
    assert bytes([(144+y)&255,t,a,(120+x)&255])in[oam[j:j+4]for j in range(0,256,4)]
   rows.append(dict(facing=face,P=p,callback_C=94,firstrecord_C=95,record=hex(ptr),source_returnX=c.x,original_parts=len(sourceparts),host_parts=6))
  checks['death_actual_callback_C94_to_firstrecord_C95']=rows
  # Actual source lethal continuation and native KillPlayer clock/lose-life
  # consumer. 180/150 is explicitly SMB host timing, not source-room timing.
  rows=[]
  for pit in [0,1]:
   m=make(b);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x10,0]);put(m,NumberofLives=2)
   if not pit:target(m);d.call(m,'InjurePlayer',sp=224)
   else:put(m,Player_Y_Position=245);d.call(m,'MegaManCheckPit',sp=224)
   assert get(m,'GameEngineSubroutine')==11 and get(m,'MmDeathFlag')==1 and m[0x5c00]==7
   c,low,tr=d.call(m,'PlayerDeath',sp=224);minimum=min(minimum,low)
   assert m[0x5c03]==53 and m[0x5c01]==m[0x5c02]==0
   expected=150 if pit else 180
   for age in range(1,expected):d.call(m,'PlayerDeath',sp=224)
   assert get(m,'GameEngineSubroutine')==6 and get(m,'TimerControl')==0
   d.call(m,'PlayerLoseLife',sp=224);assert get(m,'NumberofLives')==1
   # Native current life receipt is consumed at real next-area target.
   d.call(m,'RdLifeArea',sp=224)
   assert list(m[0x5fb0:0x5fb6])==[255,7,15,3,0x99,0x39]
   rows.append(dict(pit=pit,native_death_updates=expected,lives_after=1,persistent_after=list(m[0x5fb0:0x5fb6]),minimum_SP=low))
  checks['source_lethal_to_native_death_life_reset']=rows
  rows=[]
  for pit in[0,1]:
   m=make(b);put(m,NumberofLives=2)
   if pit:put(m,Player_Y_Position=245)
   else:m[0x5fb4:0x5fb6]=bytes([0x10,0]);target(m,6,1)
   cpu,row=mainstep(m,first=True);minimum=min(minimum,row['minimum_SP'])
   assert get(m,'GameEngineSubroutine')==11 and m[0x5c00]==7
   m[address(b,'Enemy_Flag')]=0
   expected=150 if pit else 180;frames=[];minimum_case=row['minimum_SP']
   for age in range(1,expected+1):
    cpu,row=mainstep(m);minimum_case=min(minimum_case,row['minimum_SP']);minimum=min(minimum,row['minimum_SP'])
    assert get(m,'GameEngineSubroutine')==(6 if age==expected else 11)
    frames.append(m[0x5c03])
   cpu,row=mainstep(m);minimum=min(minimum,row['minimum_SP'])
   assert get(m,'NumberofLives')==1 and get(m,'OperMode_Task')==0
   rows.append(dict(pit=pit,complete_Main_death_updates=expected,death_animation_frames=sorted(set(frames)),minimum_SP=minimum_case,real_native_life_loss=True))
  checks['continuous_full_Main_NMI_death_clock_and_real_life_loss']=rows
  # Actual1Up increment owner, never a mismatch-based equipment reset.
  m=make(b);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x12,0x19]);before=bytes(m[0x5fb0:0x5fb6]);put(m,NumberofLives=2)
  m[address(b,'FloateyNum_Control')]=11;m[address(b,'FloateyNum_Timer')]=0x2b
  d.call(m,'FloateyNumbersCore',sp=224,x=0)
  assert get(m,'NumberofLives')==3 and bytes(m[0x5fb0:0x5fb6])==before
  checks['actual_1Up_gain_preserves_all_resources']=dict(lives_before=2,lives_after=3,persistent=list(before))
  # Native pause bypasses real control; no source timers/recovery animation.
  m=make(b);m[0x5c1c]=31;put(m,GamePauseStatus=1)
  before=bytes(m[0x5c00:0x5c80]);c,row=mainstep(m,first=True)
  assert bytes(m[0x5c00:0x5c80])==before
  checks['actual_Main_pause_source_state_exact']=True
  proof.update(passed=True,minimum_SP=minimum,limits=['CPU source components only; no native hardware/PPU/deadline/audio/playable proof.','Actual identity is raw2/RdVariant1; private menu toggle/admission is not installed by this unit.','Typed ordinary enemy contact8HP is explicit SMB adaptation using source arithmetic; hazards/bosses/unknown return protected and remain NOT qualified.','Native180/150 death clock is an explicit SMB life-transition adaptation, not original Rogue room timing.','Constructor/mature pickup/gear and source weapon/actor-effect integration and authentic audio remain OPEN.'])
 except BaseException as e:
  proof.update(error=str(e),traceback=traceback.format_exc());raise
 finally:
  proof['bindings']=[ref.binding(p)for p in[Path(__file__),R/'src/rogue_dawn_host_lifecycle.s',O/'build.json',O/'candidate.nes',O/'candidate.dbg',P,P.with_suffix('.dbg'),R/'build/rogue-dawn-death-art-v1/handoff.json',R/'tools/rogue_dawn_host_body_controls_v1.py']]
  (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,counts={k:len(v)if isinstance(v,list)else v for k,v in checks.items()},minimum_SP=minimum)))
if __name__=='__main__':main()
