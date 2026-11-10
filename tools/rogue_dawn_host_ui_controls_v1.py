"""Finite actual CPU menu/HUD caller/progress controls, never native proof."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_weapons_controls_v1 as w
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import run,app,registers,cleanwrites
from proto_palette_coalesce_controls_v1 import ppu
O=R/'build/rogue-dawn-host-ui-v1';P=R/'build/rogue-dawn-host-hazards-v1'
get,put,call=w.get,w.put,w.call
def packet(m):
 at=address(m.bundle,'VRAM_Buffer1');return bytes(m[at:at+get(m,'VRAM_Buffer1_Offset')+1])
def ready(b,health=(0x99,9),missiles=5):
 m=w.life.make(b);put(m,NmiDisable=0,DisableScreenFlag=0,TimerControl=0,VRAM_Buffer_AddrCtrl=0,ReloadCHRBank=0,RdColorRequest=0,InvDirty=1,RdHealthLo=health[0],RdHealthHi=health[1],RdMissiles=missiles,InvHudActive=0)
 for n in ['VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer1','VRAM_Buffer2','AreaParserTaskNum','ScrollThirtyTwo','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','GamePauseStatus']:put(m,**{n:0})
 return m
def expect(m):
 hi=get(m,'RdHealthHi');lo=get(m,'RdHealthLo');ms=get(m,'RdMissiles')
 return bytes([32,35,11,14,hi>>4,hi&15,lo>>4,36,22,ms//100,ms//10%10,ms%10,36,36,0])
def consume(m):
 """Genuine full regular NMI ordered bus, no display/timing certification."""
 m.writes.clear();low=w.life.wake(m);image,bus=ppu(m.writes);return low,image,bus
def step(m,keys=0,first=False,seam=None):
 # Actual source CPU arena: supply pad byte at its genuine saved-controller
 # boundary after NMI, never motion/resource/outcome state. Native remains open.
 if not first:w.life.wake(m)
 put(m,SavedJoypadBits=keys)
 return w.life.mainstep(m,first=True,seam=seam)
def snap(m,c):
 class Q:pass
 q=Q();q.b=m.bundle;q.m=m
 return registers(c),app(q),tuple(m.banks)
def main():
 b=w.life.d.old.scoped_load(O/'candidate.nes');old=w.life.d.old.scoped_load(P/'candidate.nes');checks={};minimum=255
 proof=dict(passed=False,source_CPU_only=True,native_run=False,ROM=w.ref.binding(O/'candidate.nes'),checks=checks)
 try:
  rows=[]
  for health,ms,p in itertools.product([(0,0),(0x09,0),(0x99,0),(0x99,9),(0,0x10),(0x99,0x69)],range(256),[0x30,0x71]):
   m=ready(b,health,ms);want=expect(m);c,l,tr=call(m,'RdUiLateReset',a=91,x=17,y=23,p=p);minimum=min(minimum,l)
   assert packet(m)==want and get(m,'InvDirty')==0
   assert [get(m,'InvHudName'),get(m,'InvHudName',1),get(m,'InvHudAmmo')]==[health[0]&240,health[1],ms]
   # Actual old ResetPalStar owns return A/N/Z; wrapper preserves its outputs.
   q=ready(b,health,ms);d,_,_=call(q,'ResetPalStar',a=91,x=17,y=23,p=p)
   # Different direct entries necessarily map different incoming A windows;
   # whole GameLoop compares the true same-caller bank restoration separately.
   assert registers(c)==registers(d),(registers(c),registers(d))
   if ms in[0,5,99,100,255]and health==(0x99,9)and p==0x30:
    low,image,bus=consume(m);minimum=min(minimum,low)
    assert bytes(image[a]for a in range(0x2023,0x202e))==want[3:14]
    rows.append(dict(health=list(health),missiles=ms,packet=list(want),actual_NMI_HUD_writes=[list(z)for z in bus if 0x2023<=z[0]<0x202e]))
  checks['actual_late_packet_all_binary_ammo_source_BCD_and_full_return']=dict(cases=6*256*2,representative_actual_NMI_bus=rows)
  rows=[]
  guards=['DisableScreenFlag','TimerControl','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer1','VRAM_Buffer2','ReloadCHRBank','RdColorRequest','SmFreezePalettePending','InvHudActive','StarInvincibleTimer','GuestPowerupActive','PlayerChangeSizeFlag','AreaParserTaskNum','GamePauseStatus']
  for n in guards:
   m=ready(b);put(m,**{n:1});before=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]);cache=bytes(m[address(b,'InvHudName'):address(b,'InvHudName')+2])+bytes([get(m,'InvHudAmmo')])
   c,l,tr=call(m,'RdUiLateReset');assert before==bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])and get(m,'InvDirty')==1
   assert cache==bytes(m[address(b,'InvHudName'):address(b,'InvHudName')+2])+bytes([get(m,'InvHudAmmo')]);rows.append(n)
  for n,value in [('OperMode',0),('GameEngineSubroutine',11),('ScrollThirtyTwo',32),('ScrollThirtyTwo',255)]:
   m=ready(b);put(m,**{n:value});call(m,'RdUiLateReset');assert get(m,'InvDirty')==1 and get(m,'VRAM_Buffer1_Offset')==0;rows.append([n,value])
  checks['dirty_preserved_all_actual_queue_CHR_control_later_parser_predicates']=rows
  rows=[]
  # Complete old command must be byte/cache-identical; no approximate removal.
  for ms in[0,5,99,100,199,255]:
   m=ready(b,missiles=ms);call(m,'RdUiLateReset');full=packet(m)
   for i in range(15):
    for bit in[1,16,128]:
     n=ready(b,missiles=ms);call(n,'RdUiLateReset');n[address(b,'VRAM_Buffer1')+i]^=bit;before=packet(n)
     call(n,'RdUiEarly');assert packet(n)==before and get(n,'InvDirty')==0,(ms,i,bit,full,before,packet(n))
   for name,index in [('InvHudName',0),('InvHudName',1),('InvHudAmmo',0)]:
    n=ready(b,missiles=ms);call(n,'RdUiLateReset');n[address(b,name)+index]^=16;before=packet(n);call(n,'RdUiEarly');assert packet(n)==before
   call(m,'RdUiEarly');assert packet(m)==bytes([0])and get(m,'InvDirty')==1
   rows.append(dict(ammo=ms,accepted_exact=list(full),each_of15bytes_rejects_three_bit_changes=True,wrong_cache_rejected=True))
  m=ready(b,missiles=43);call(m,'RdUiLateReset');m[address(b,'VRAM_Buffer1')+9:address(b,'VRAM_Buffer1')+12]=bytes([2,9,9]);before=packet(m);call(m,'RdUiEarly');assert packet(m)==before
  checks['sole_owned_lag_packet_retraction_and_negative_signatures']=dict(accepted=len(rows),mutated_bytes=6*15*3,wrong_cache=18,overflow299_vs43_rejected=True,rows=rows)
  print('leaf packets, admission and exact retraction pass',flush=True)
  # Genuine source Main/NMI progress. Cold/newlife palette/CHR work is NOT
  # removed or seeded empty; stable page terrain/actual pad input are explicit.
  progress=[]
  for mode,keys in itertools.product([0,1],[0,1]):
   m=w.life.make(b,mode);put(m,DisableScreenFlag=0);call(m,'NrFreshGameInit');events=[];seen=[];xs=[];source_states=[]
   for tick in range(96):
    c,row=step(m,keys,first=tick==0);minimum=min(minimum,row['minimum_SP']);xs.append(get(m,'Player_X_Position')+256*get(m,'Player_PageLoc'))
    events.append(dict(tick=tick,worldX=xs[-1],queue=list(packet(m)),Reload=get(m,'ReloadCHRBank'),dirty=get(m,'InvDirty'),parser=get(m,'AreaParserTaskNum'),scroll=get(m,'ScrollThirtyTwo')))
    if packet(m)==expect(m):seen.append(tick)
    source_states.append([get(m,'RdAnimFrame'),get(m,'RdAction'),get(m,'CurrentCHRBank')])
   assert seen and seen[0]<=8,('cold HUD starvation',mode,keys,events)
   assert keys==0 or max(xs)>min(xs)+32,('not actual walking',mode,xs)
   # Real source damage -> dirty display update without direct health/cache seed.
   if keys==0:
    hp=bytes(m[0x5fb4:0x5fb6])
    call(m,'RdHsDamage',a=0x80)
    assert bytes(m[0x5fb4:0x5fb6])!=hp
   else:
    # A real missile tank grant provides ammo then its source debit changes it.
    call(m,'RdHsGrantType',a=9);step(m,32);step(m,64)
    assert get(m,'RdMissiles')==4 and get(m,'RdMissileMode')==1
   before=get(m,'InvHudName'),get(m,'InvHudName',1),get(m,'InvHudAmmo');committed=[]
   for tick in range(32):
    c,row=step(m,keys);minimum=min(minimum,row['minimum_SP'])
    if packet(m)==expect(m):committed.append(tick);break
   assert committed,('earned change HUD starvation',mode,keys,before,list(m[0x5fb0:0x5fb6]))
   low,image,bus=consume(m);minimum=min(minimum,low);assert all(a in image for a in range(0x2023,0x202e))
   progress.append(dict(mode=mode,controller=keys,complete_Mains=96,worldX_range=[min(xs),max(xs)],cold_commit_ticks=seen,after_real_change_commit=committed[0],actual_NMI_HUD_bus=[list(z)for z in bus if 0x2023<=z[0]<0x202e],first12=events[:12],source_pose_CHR_states=sorted(set(map(tuple,source_states)))))
  checks['consecutive_actual_Main_idle_walking_eventual_dirty_and_delivered_NMI']=progress
  print('real idle/walking Main progress pass',flush=True)
  # The actual retained optional command goes through genuine lagNMI first.
  # Next complete Main must retract it BEFORE native native timer/palette/CHR
  # producers; pending parser/CHR may delay retry but may not ack stale cache.
  rows=[]
  for keys,seam in itertools.product([0,1],['none','timer','CHR','parser']):
   m=w.life.make(b);put(m,DisableScreenFlag=0);call(m,'NrFreshGameInit')
   for tick in range(12):
    c,row=step(m,keys,first=tick==0)
    if packet(m)==expect(m):break
   else:raise AssertionError('no original committed packet')
   prior=packet(m);put(m,NmiDisable=255);low,image,bus=consume(m);assert packet(m)==prior and not any(0x2023<=a<0x202e for a,v in bus)
   if seam=='timer':put(m,GameTimerCtrlTimer=0)
   elif seam=='CHR':put(m,ReloadCHRBank=1)
   elif seam=='parser':put(m,ScrollThirtyTwo=32)
   visits=[];oldstep=NesMPU.step
   def trace(cpu):
    bank=m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
    if bank==121 and cpu.pc in[address(b,'RdUiEarly'),address(b,'RdUiEarly::Done'),address(b,'RdUiLateReset')]:visits.append(dict(PC=hex(cpu.pc),queue=list(packet(m)),dirty=get(m,'InvDirty')))
    oldstep(cpu)
   NesMPU.step=trace
   try:c,row=step(m,keys,first=True)
   finally:NesMPU.step=oldstep
   minimum=min(minimum,row['minimum_SP']);assert visits[0]['queue']==list(prior)
   done=[z for z in visits if z['PC']==hex(address(b,'RdUiEarly::Done'))];assert done and done[0]['queue']==[0]and done[0]['dirty']==1,visits
   p=packet(m);assert p[:3]!=prior[:3]or p==expect(m),('partly combined HUD queue',seam,list(p))
   retry=[]
   for tick in range(40):
    if packet(m)==expect(m):retry.append(tick);break
    c,row=step(m,keys);minimum=min(minimum,row['minimum_SP'])
   assert retry,('post-lag starvation',keys,seam,visits)
   rows.append(dict(keys=keys,next_real_work=seam,lag_retained_exact=list(prior),actual_early_late_observations=visits,retry_after_Mains=retry[0]))
  checks['actual_lagNMI_next_Main_retraction_before_native_producers_then_progress']=rows
  print('lag retained queue / actual next Main producer seam pass',flush=True)
  rows=[]
  for mode,variant in itertools.product([0,1],[0,1]):
   m=w.life.make(b,mode);m[0x5fee]=variant;resource=bytes(m[0x5fb0:0x5fb6]);put(m,OperMode=0,CrossoverMenuState=2,CrossoverMenuIndex=2,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,DisableScreenFlag=0,InvHudActive=1,RdSourceAltPalette=1,RdMissileMode=1)
   for i in range(4):w.field(m,'InvDropKind',[128,129,137,1][i],i)
   c,l,tr=call(m,'CrossoverMenuInput',sp=240);minimum=min(minimum,l)
   assert get(m,'SelectedCharacter')==2 and get(m,'RdVariant')==1-variant and get(m,'InvHudActive')==0
   assert get(m,'RdSourceAltPalette')==get(m,'RdMissileMode')==0
   assert bytes(m[0x5fb0:0x5fb6])==resource and [get(m,'InvDropKind',i)for i in range(4)]==[0,0,0,1]
   if variant==0:
    assert bytes([32,32,32])!=packet(m)[9:12] # actual encoded native name follows palette
    assert bytes([36,36,36,27,24,16,30,14,36,13,10,32,23,36,36,36])in packet(m)
    assert get(m,'RdAnimFrame')==8 and get(m,'SmChrBank')==169
   rows.append(dict(mode=mode,from_variant=variant,to_variant=get(m,'RdVariant'),queue=list(packet(m)),minimum_SP=l,resources_unchanged=True,raw_selected=2))
  checks['real_same_slot_menu_Select_and_name_portrait_cleanup']=rows
  for kind in range(256):
   m=w.life.make(b);put(m,CrossoverMenuPressed=32);w.field(m,'InvDropKind',kind,3);call(m,'RdUiToggle')
   assert get(m,'InvDropKind',3)==(0 if kind in[128,129,137]else kind)
  checks['variant_change_only_three_actual_private_drop_kinds']=dict(cases=256,cleared=[128,129,137],all_unknown_and_legacy_retained=True)
  rows=[]
  for context,p in itertools.product(['DrawSelectionPreview','DisplayIntermediate'],w.life.body.FLAGS):
   m=w.life.make(b);resource=bytes(m[0x5fb0:0x5fb6]);active=bytes(m[0x5c00:0x5c80]);put(m,OperMode=0 if context=='DrawSelectionPreview' else 1,DisableIntermediate=0,AltEntranceControl=0,PlayerStatus=1,CurrentOAMOffset=0)
   c,l,tr=call(m,context,a=91,x=17,y=23,p=p,sp=240);minimum=min(minimum,l)
   assert bytes(m[0x5fb0:0x5fb6])==resource and m.banks[2]==94 and get(m,'RdAnimFrame')==8 and get(m,'ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY')
   assert get(m,'CurrentOAMOffset')>0 and get(m,'SmChrBank')==169
   assert get(m,'RdAction')==active[0]and get(m,'RdVY')==active[8]
   rows.append(dict(caller=context,P=p,actual_C=m.banks[2],OAMbytes=get(m,'CurrentOAMOffset'),minimum_SP=l))
  checks['real_menu_lives_direct_SamusPortrait_then_genuine_first_reader']=rows
  rows=[]
  for a,p in itertools.product([0,1,2,3],w.life.body.FLAGS):
   m=w.life.make(b);at=address(b,'VRAM_Buffer1');m[at:at+84]=bytes([0x59]*84);before=bytes(m[at:at+84]);c,l,tr=call(m,'LmStatusNameGate',a=a,x=17,y=23,p=p)
   assert m[at+18]==0x59 and bytes(m[at+18:at+84])==before[18:]
   assert bytes(m[at+11:at+18])==(bytes([27,24,16,30,14,36,36])if a==0 else before[11:18])
   assert c.x==17 and c.y==23 and c.a==(0 if a==0 else a)
   rows.append([a,p,l])
  checks['real_status_name_exact7_canary_following_WORLD_command']=dict(cases=len(rows))
  print('actual menu/lives/status caller pass',flush=True)
  proof.update(passed=True,minimum_SP=minimum,limits=['CPU/source-only. No native timing, physical display/pixels, menu or audio admission.','Actual pad bytes supplied at saved-controller source boundary; source Main+NMI campaigns are not native routes.','Rogue menu/lives/UI adaptation is authored native font/scaled source data, not original Rogue UI or hue/audio fidelity.'])
 except BaseException as e:
  proof.update(error=str(e),traceback=traceback.format_exc())
  with (O/'preparation-negatives.jsonl').open('a')as f:f.write(json.dumps(dict(ROM=proof['ROM']['sha256'],error=str(e),traceback=traceback.format_exc()))+'\n')
  raise
 finally:
  proof['bindings']=[w.ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',R/'src/rogue_dawn_host_ui_gate_v1.s',R/'src/rogue_dawn_host_ui_v1.s',R/'tools/rogue_dawn_host_lifecycle_controls_v1.py',R/'tools/audit/proto_palette_coalesce_controls_v1.py']]
  (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,minimum_SP=minimum,sections=len(checks))))
if __name__=='__main__':main()
