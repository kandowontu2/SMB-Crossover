"""Actual native bbox/position primitives and private DK Jr ground-carry event."""
import itertools,json,re
from pathlib import Path
import prepare_dkjr_native_carry_1102_v4 as P
import check_hogan_current_bounded_v1 as N
R=P.R;O=P.O;D=P.P.P.D


def main():
 b=P.P.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=P.P.CURRENT.read_bytes();assert P.P.P.sha(raw)==P.P.PIN;b['raw']=raw
 q=json.loads((O/'native-carry-v4-layout.json').read_text());blob=(O/'native-carry-v4.bin').read_bytes();assert P.P.P.sha(blob)==q['code_SHA256'];lab=q['labels'];minimum_sp=255
 seed,_=D.active();seed=bytes(seed.memory[:2048]);counts={};cycles=[]
 def put(m,name,value,i=0):m[N.address(b,name)+i]=value
 def get(m,name,i=0):return m[N.address(b,name)+i]
 def call(m,name,a=0x57,x=7,y=9,p=0xf1):
  nonlocal minimum_sp
  c=N.NesMPU(memory=m,pc=lab[name]);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe)
  for _ in range(100000):
   if c.pc==0x5fff:break
   minimum_sp=min(minimum_sp,c.sp);assert m[c.pc]!=0,('private/native BRK',hex(c.pc),m.rawtags);c.step()
  else:raise AssertionError(('private/native bound',name,hex(c.pc)))
  assert c.sp==224;return dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles)
 def fresh(camera=256):
  m=N.Bus(b);m.ram[3][:len(blob)]=blob;m.ram[2][:2048]=seed;m.raw_page(1,3);m.raw_page(2,2)
  N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,GameEngineSubroutine=8,TimerControl=0,AreaPointer=0,WorldNumber=0,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8,ObjectOffset=4)
  call(m,'DkjrUseOriginalGeometry')
  return m
 # These are actual native primitive fixtures on Mario0, not functional new
 # rawID/public-policy rows. The private DK event is invoked separately.
 refresh_rows=[]
 for camera,flags in itertools.product([0,1,15,127,248,255,256,511],[0x30,0x71,0xf1]):
  m=fresh(camera)
  for i,ident in enumerate([0x24,0x25,0x28,0x2a,0x2b,0x2c]):
   world=camera+16+i*32
   for n,v in[('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0x60 if i==2 else 0),('Enemy_X_Position',world&255),('Enemy_PageLoc',world>>8),('Enemy_Y_Position',80+i*16),('Enemy_Y_HighPos',1),('SprObj_BoundBoxCtrl',4 if i>=4 else 5)]:put(m,n,v,i+1 if n=='SprObj_BoundBoxCtrl'else i)
   for j in range(4):m[N.address(b,'BoundingBox_UL_Corner')+4*(i+1)+j]=7
  reference=N.fork(m)
  for i in range(5,-1,-1):
   put(reference,'ObjectOffset',i)
   for name in['GetEnemyOffscreenBits','RelativeEnemyPosition','SmallPlatformBoundBox'if get(reference,'Enemy_ID',i)>=0x2b else'HpNativePlatformBBoxGate']:N.invoke(reference,name,x=i)
  before=bytes(m.ram[2]);scratch=bytes(m[N.address(b,'R0'):N.address(b,'R0')+8]);smc=bytes(m[0x15a:0x17b]);maps=list(m.rawtags);offset=get(m,'ObjectOffset');z=call(m,'DkjrNativeRefreshPlatforms',p=flags)
  assert[z[k]for k in['A','X','Y','P']]==[0x57,7,9,flags|0x30],z
  assert maps==m.rawtags and scratch==bytes(m[N.address(b,'R0'):N.address(b,'R0')+8])and offset==get(m,'ObjectOffset')and smc==bytes(m[0x15a:0x17b])and before==bytes(m.ram[2])
  bbox=N.address(b,'BoundingBox_UL_Corner');assert m[bbox+4:bbox+28]==reference[bbox+4:bbox+28],('actual native bbox mismatch',camera,flags)
  for i in range(6):assert m[bbox+4*(i+1)+1]==80+i*16
  refresh_rows.append(dict(camera=camera,P=flags,cycles=z['CPU']));cycles.append(z['CPU'])
 counts['actual_native_bbox_refresh_with_maps_SMC_AXYP_scratch_private_state_preserved']=len(refresh_rows)
 inactive=[]
 for ident,flag in itertools.product([0,6,0x23,0x24,0x28,0x2c,0x2d,0x2f],[0,0x81]):
  m=fresh()
  for i in range(6):put(m,'Enemy_ID',ident,i);put(m,'Enemy_Flag',flag,i)
  low=bytes(m[:256])+bytes(m[0x200:0x800]);private=[bytes(x)for x in m.ram];maps=list(m.rawtags)
  z=call(m,'DkjrNativeRefreshPlatforms');assert[z[k]for k in['A','X','Y','P']]==[0x57,7,9,0xf1]
  assert bytes(m[:256])+bytes(m[0x200:0x800])==low and private==[bytes(x)for x in m.ram]and maps==m.rawtags
  inactive.append(z['CPU'])
 counts['empty_or_nonprimary_objects_skip_all_native_bbox_calls']=len(inactive)
 # CurrentBBox must be refreshed before source support queries. The previous
 # native loop can publish a bbox and then move the platform afterward.
 current_boxes=0
 for old_y,new_y in[(208,207),(207,208),(144,146),(160,158)]:
  m=fresh();world=320
  for n,v in[('Enemy_Flag',1),('Enemy_ID',0x28),('Enemy_State',0x40),('Enemy_X_Position',world&255),('Enemy_PageLoc',world>>8),('Enemy_Y_Position',new_y),('Enemy_Y_HighPos',1),('SprObj_BoundBoxCtrl',5)]:put(m,n,v,1 if n=='SprObj_BoundBoxCtrl'else 0)
  bbox=N.address(b,'BoundingBox_UL_Corner')+4
  for j,v in enumerate([64,old_y,96,old_y+8]):m[bbox+j]=v
  call(m,'DkjrNativeRefreshPlatforms');assert m[bbox+1]==new_y
  N.put(m,Player_X_Position=72,Player_PageLoc=1,Player_Y_Position=new_y-32,Player_Y_HighPos=1)
  call(m,'DkjrNativeImportAnchor');call(m,'DkjrNativeWorldEnable');call(m,'DkjrBounds');z=call(m,'D_e89f');assert z['A']!=0 and m.ram[2][0x43]==new_y
  current_boxes+=1
 counts['refresh_current_native_platform_before_original_support_probe']=current_boxes
 carry_rows=[]
 for camera,dx,top in itertools.product([0,255,256,511],[-2,-1,0,1,2],[144,160,208]):
  m=fresh(camera);world=camera+72
  N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=top-32,Player_Y_HighPos=1)
  for n,v in[('Enemy_Flag',1),('Enemy_ID',0x28),('Enemy_Y_Position',top),('Enemy_Y_HighPos',1)]:put(m,n,v,2)
  call(m,'DkjrNativeImportAnchor');m.ram[2][0x6b]=1;before=bytes(m.ram[2][:2048]);put(m,'R0',dx&255);put(m,'ObjectOffset',2)
  N.invoke(m,'PositionPlayerOnHPlat',x=2);assert get(m,'Player_X_Position')+256*get(m,'Player_PageLoc')==(world+dx)&65535 and get(m,'Player_Y_Position')==top-32
  native_before=bytes(m[:256])+bytes(m[0x200:0x800]);z=call(m,'DkjrNativeCarryEvent',x=2);assert z['P']&1
  expected=bytearray(before)
  for i in range(0,32,4):expected[0x213+i]=(expected[0x213+i]+dx)&255
  assert bytes(m.ram[2][:2048])==expected,('ground carry altered original phase/fractions',camera,dx,top)
  assert bytes(m[:256])+bytes(m[0x200:0x800])==native_before
  # Repeated notification of the identical actual position is idempotent.
  call(m,'DkjrNativeCarryEvent',x=2);assert bytes(m.ram[2][:2048])==expected
  carry_rows.append(dict(camera=camera,native_delta_x=dx,top=top,original_fractions_preserved=True))
 counts['actual_native_horizontal_position_then_typed_ground_carry']=len(carry_rows)
 small=0
 for area,worldno,which in itertools.product([0,0x62],[0,1,4], [1,2]):
  m=fresh();N.put(m,AreaPointer=area,WorldNumber=worldno,Player_X_Position=72,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,ObjectOffset=1)
  for n,v in[('Enemy_Flag',1),('Enemy_ID',0x2b),('Enemy_Y_Position',80),('Enemy_State',192),('Enemy_Y_HighPos',1)]:put(m,n,v,1)
  call(m,'DkjrNativeImportAnchor');m.ram[2][0x6b]=1
  N.invoke(m,'PositionPlayerOnS_Plat',a=which,x=1)
  expected_top=80 if which==2 else 192 if area==0x62 and worldno in[1,4] else 208
  assert get(m,'Player_Y_Position')==expected_top-32
  z=call(m,'DkjrNativeCarryEvent',x=1);assert z['P']&1 and m.ram[2][0x210]==expected_top-17;small+=1
 counts['actual_native_small_platform_first_second_position_events']=small
 landings=0;injuries=0
 for state,top,penetration,threshold,distance,facing in itertools.product([3,4],[144,176,208],[0,1,4],[20,22,24],[-1,0,19,20,21,22,23,24,25],[0,1]):
  m=fresh();r=bytearray(seed);pre_y=top-17+penetration
  r[0x6b]=state;r[0x6c]=state;r[0x6d]=facing;r[0x7e]=30;r[0x7b]=threshold;r[0x76]=(pre_y-distance)&255;r[0x56]=0x73;r[0x7f]=0xa5;r[0x82]=0xa0;r[0x83]=1;r[0x63]=0
  donor=D.Bus();donor[:2048]=r;donor[0]=64;donor[1]=pre_y;donor[2]=0x18
  d=D.T.NesMPU(memory=donor,pc=0);D.T.run(d,0xe9ee,facing^1,2,9,0x30);r=bytes(donor[:2048]);m.ram[2][:2048]=r
  N.put(m,Player_X_Position=72,Player_PageLoc=1,Player_Y_Position=pre_y-15,Player_Y_HighPos=1,ObjectOffset=2)
  for n,v in[('Enemy_Flag',1),('Enemy_ID',0x28),('Enemy_Y_Position',top),('Enemy_Y_HighPos',1)]:put(m,n,v,2)
  N.invoke(m,'PositionPlayerOnVPlat',x=2)
  donor[0x43]=top;D.T.run(d,0xda22,0x57,2,9,0x30)
  z=call(m,'DkjrNativeCarryEvent',x=2);assert z['P']&1
  differences=[(i,donor[i],m.ram[2][i])for i in list(range(256))+list(range(0x200,0x800))if donor[i]!=m.ram[2][i]]
  assert not differences,('original pre-snap platform landing',state,top,penetration,threshold,distance,facing,differences[:8])
  if m.ram[2][0x6b]==5:injuries+=1
  else:
   before=bytes(m.ram[2][:2048]);call(m,'DkjrNativeCarryEvent',x=2);assert before==bytes(m.ram[2][:2048]),'repeat landing reset original phase'
  landings+=1
 counts['actual_native_vertical_position_then_original_DA22_landing_parity']=landings;counts['original_pre_snap_fall_distance_injury_preserved']=injuries
 rejected=0
 for source_state,engine,timer,slot in itertools.product([0,1,2,3,4,5],[8,11],[0,1],[2,6]):
  m=fresh();N.put(m,GameEngineSubroutine=engine,TimerControl=timer,Player_X_Position=72,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1)
  for n,v in[('Enemy_Flag',1),('Enemy_ID',0x28),('Enemy_Y_Position',208),('Enemy_Y_HighPos',1)]:put(m,n,v,2)
  m.ram[2][0x6b]=source_state;before=bytes(m.ram[2][:2048]);z=call(m,'DkjrNativeCarryEvent',x=slot)
  legal=source_state in[1,3,4]and engine==8 and timer==0 and slot==2
  assert bool(z['P']&1)==legal
  if not legal:assert before==bytes(m.ram[2][:2048]);rejected+=1
 counts['unsupported_phase_scene_timer_slot_reject_before_source_mutation']=rejected
 life_cases=0
 for state,engine in itertools.product([1,2,3,4,5],[0,6,8,11]):
  m=fresh();m.ram[2][0x6b]=state;N.put(m,GameEngineSubroutine=engine,TimerControl=255,NumberofLives=2)
  private=bytes(m.ram[2][:2048]);z=call(m,'DkjrNativeLifeTerminal');accepted=state==5 and engine in[8,11]
  assert bool(z['P']&1)==accepted and bytes(m.ram[2][:2048])==private and get(m,'NumberofLives')==2
  if accepted:
   assert get(m,'GameEngineSubroutine')==6 and get(m,'TimerControl')==0 and m.ram[2][0x8f8]==1
   N.put(m,GameEngineSubroutine=8,TimerControl=123);_,before=bytes(m.ram[2]),bytes(m[:0x800]);z=call(m,'DkjrNativeLifeTerminal');assert not z['P']&1 and get(m,'GameEngineSubroutine')==8 and get(m,'TimerControl')==123
  life_cases+=1
 counts['native_death_terminal_phase_guard_and_once_only_without_direct_life_decrement']=life_cases
 terminal_epochs=[]
 for pit in[False,True]:
  m=fresh();N.put(m,NumberofLives=2,GameEngineSubroutine=8,TimerControl=0)
  r=bytearray(seed);r[0x6b]=5;r[0x64]=0 if pit else 3;r[0x65]=0 if pit else 0x24
  if pit:
   for i in range(0,32,4):r[0x210+i]=216+(8 if i&4 else 0)
   r[8]=0
  m.ram[2][:2048]=r
  # Compare each exact original defeat tick until the external CF62 seam;
  # original donor life bookkeeping is deliberately not executed afterward.
  for epoch in range(300):
   before=bytes(m.ram[2][:2048]);donor=D.Bus();donor[:2048]=before;d=D.T.NesMPU(memory=donor,pc=0xcf37);d.a,d.x,d.y,d.p,d.sp=0x57,2,9,0x30,224;d.stPushWord(0x5ffe)
   for _ in range(100000):
    if d.pc in[0xcf62,0x5fff]:break
    assert donor[d.pc]!=0;d.step()
   else:raise AssertionError('Original defeat tick bound')
   is_terminal=d.pc==0xcf62
   call(m,'DkjrDefeatTick',x=2,p=0x30)
   diff=[(i,donor[i],m.ram[2][i])for i in list(range(256))+list(range(0x200,0x800))if donor[i]!=m.ram[2][i]];assert not diff,('original defeat terminal phase',pit,epoch,diff[:8])
   if is_terminal:
    assert get(m,'GameEngineSubroutine')==6 and m.ram[2][0x8f8]==1 and get(m,'NumberofLives')==2
    terminal_epochs.append(dict(pit=pit,exact_original_terminal_epoch=epoch+1));break
  else:raise AssertionError('Original defeat never reached native terminal')
 counts['original_defeat_progression_stops_only_at_CF62_native_handoff']=terminal_epochs
 lost_lives=[]
 for initial_lives in[0,1,2]:
  m=fresh();m.ram[2][0x6b]=5;N.put(m,NumberofLives=initial_lives,NumberOfPlayers=0,CurrentPlayer=0,WorldNumber=0,LevelNumber=0,ScreenLeft_PageLoc=1,OperMode=1,OperMode_Task=3,TimerControl=255)
  call(m,'DkjrNativeLifeTerminal');assert get(m,'NumberofLives')==initial_lives and get(m,'GameEngineSubroutine')==6
  N.invoke(m,'PlayerLoseLife');assert get(m,'NumberofLives')==(initial_lives-1)&255
  if initial_lives==0:assert get(m,'OperMode')==3
  lost_lives.append(dict(initial=initial_lives,final=get(m,'NumberofLives'),mode=get(m,'OperMode')))
 counts['actual_native_PlayerLoseLife_checkpoint_gameover_bookkeeping']=lost_lives
 result=dict(passed=True,native_run=False,native_owner_admitted=False,ROM_written=False,base_ROM_SHA256=P.P.PIN,component_SHA256=q['code_SHA256'],component_bytes=len(blob),header_reserved_spare=q['header_reserved_spare'],checks=counts,refresh_CPU_cycles=dict(six_platforms_minimum=min(cycles),six_platforms_maximum=max(cycles),no_active_platforms_minimum=min(inactive),no_active_platforms_maximum=max(inactive)),minimum_CPU_SP=minimum_sp,remaining_imports=10,carry_endpoint_unwired=True,scope='Actual current native bbox/position functions execute in isolated legal Mario0 primitive fixtures, then private DK carry/landing; source-air/fall fixtures compare original DA22 pre-snap injury. Original defeat ticks reach CF62 before exact native EndDeath/PlayerLoseLife handoff. No new rawID/public rows or shared gate exists; actual event/sourceDY admission, owner/Main/fruit/contact/render/ISR remain unqualified.',bindings={p.relative_to(R).as_posix():P.P.P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-carry-v4.bin',O/'native-carry-v4.s',O/'native-carry-v4-layout.json']})
 (O/'native-carry-v4-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
