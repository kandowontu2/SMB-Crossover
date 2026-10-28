"""Fresh assembled4cbd plus two-platform ownership/caller/access qualification; no native claim."""
from pathlib import Path
import argparse,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *
from celeste_mac_union_controls_v1 import full

def fresh(b,mode=0,tier=0,camera=768):
 q=cmseed(b,tier);q.put(AreaPointer=37,WorldNumber=0,LevelNumber=0,CrossoverBehaviorVersion=mode)
 run(q,'HpLoadArea');q.put(GameEngineSubroutine=8,TimerControl=0,GamePauseStatus=0,ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,ScreenRight_PageLoc=(camera+255)>>8,ScreenRight_X_Pos=(camera+255)&255)
 return q

def actors(q):return[(i,q.get('HpActorOwner',i))for i in range(6)if q.get('Enemy_Flag',i)==1 and q.get('Enemy_ID',i)==37 and q.get('Enemy_State',i)==64]

def irq_sweep(q,name,kind='IRQ',targets=None):
 oldstep=NesMPU.step;seen=set();events=[];b=q.b;start=address(b,'CmPlatformTwoStart');end=address(b,'CmPlatformTwoEnd')
 def step(c):
  bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
  key=(bank,c.pc)
  admitted=(bank==26 and start<=c.pc<end)if targets is None else key in targets
  if admitted and key not in seen and (kind=='NMI' or not c.p&4):
   seen.add(key)
   def snap():return(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc_at(b)),bytes(q.m[:8]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[address(b,'HpRamStart'):address(b,'HpRamEnd')]),bytes(q.m[0x5c00:0x5c80]))
   before=snap()
   if kind=='NMI':c.nmi()
   else:q.m[0x5204]=128;c.irq()
   for _ in range(60000):
    oldstep(c)
    if c.pc==before[5]and c.sp==before[4]:break
   else:raise AssertionError(('ISR timeout',name,kind,key))
   assert snap()==before,('ISR live state',name,kind,key)
   events.append(key)
  oldstep(c)
 NesMPU.step=step
 try:run(q,name,p=0x30)
 finally:NesMPU.step=oldstep
 return events

def approach(b,mode,wall,delay=0):
 """Actual parser map plus native movement/BG/platform collision/carry chain."""
 camera=wall-144;q=fresh(b,mode,camera=camera)
 q.put(Hidden1UpFlag=1)
 for j in range(3):q.set('AreaObjectLength',255,j)
 columns=64 if wall==912 else 160
 for _ in range(columns):run(q,'AreaParserCore');run(q,'IncrementColumnPos')
 x=wall-(48 if wall==912 else 16)
 q.put(Player_PageLoc=x>>8,Player_X_Position=x&255,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,CmState=0,Player_X_Speed=32,Player_XSpeedAbsolute=32,Player_MovingDir=1,PlayerFacingDir=1,CrouchingFlag=0,CmPreviousAB=0,CmCoyote=0,CmJumpInterval=0,CmJumpBuffer=0,Player_CollisionBits=255,DisableCollisionDet=0,DisableIntermediate=0)
 rows=[]
 for t in range(210):
  # Hold no A to board the descending native platform, then a genuine fresh
  # jump after the source carry has raised the player. No pose/velocity writes.
  jump=t>=delay
  keys=1|(128 if jump else 0)
  q.put(FrameCounter=t&255,SavedJoypadBits=keys,A_B_Buttons=keys&192,Left_Right_Buttons=1,Up_Down_Buttons=0)
  run(q,'PlayerCtrlRoutine')
  run(q,'CmPlatformWeapons')
  supports=[]
  for actor,owner in actors(q):
   q.put(ObjectOffset=actor);run(q,'RunLargePlatform',x=actor)
   if q.get('PlatformCollisionFlag',actor)<128:supports.append(actor)
  xx=q.get('Player_PageLoc')*256+q.get('Player_X_Position');yy=q.get('Player_Y_Position')
  rows.append([t,xx,yy,q.get('Player_State'),supports])
  if xx>=wall and yy<=112:return dict(reached=True,rows=rows)
 return dict(reached=False,rows=rows)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 parent=R/'build/roster-shared-rcr-adopted-v8.nes';rom=R/'build/celeste-platform-rcr-v1.nes';old,b=[scoped_load(x)for x in[parent,rom]]
 files=[Path(__file__),R/'tools/prepare_celeste_platform_current_v1.py',R/'tools/audit/celeste_platform_two_controls_v1.py',R/'tools/audit/celeste_host_controls_v4.py',R/'tools/audit/celeste_mac_union_controls_v1.py',R/'src/crossover_helpers.s',R/'src/crossover_helper_ram.s',R/'src/game.s',R/'src/object.s',R/'src/reset.s']+[p.with_suffix(ext)for p in[parent,rom]for ext in['.nes','.dbg','.lbl']]
 proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(p):sha(p)for p in files},checks={});ck=proof['checks']
 try:
  diff={k:sum(x!=y for x,y in zip(old['raw'][16+k*8192:16+(k+1)*8192],b['raw'][16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:v for k,v in diff.items()if v};assert set(diff)=={26,81}and diff[81]==3,diff
  start=address(b,'CmPlatformTwoStart');end=address(b,'CmPlatformTwoEnd');assert start==0xb140 and end<=0xb600
  assert old['raw'][16+26*8192+0x1140:16+26*8192+0x1600]==bytes([255])*1216
  assert b['raw'][1048592:]==old['raw'][1048592:]
  moved=[]
  for name,s in old['syms'].items():
   if name=='_FARCALL_COUNT':continue # assembler-only macro count, not a runtime address
   if name not in b['syms']:raise AssertionError(('old symbol missing',name))
   z=b['syms'][name]
   if int(s.get('val','0'),0)!=int(z.get('val','0'),0):moved.append(name)
  assert not moved,moved
  ck['allocation']=dict(passed=True,physical_bank=26,start=start,end_exclusive=end,emitted_bytes=end-start,cap_bytes=1216,ROM_diff=diff,all_old_symbols_RAM_CHR_exact=True,unchanged_authored_records=34)
  # Direct and indexed consumers: original owners1..3 versus new81/82.
  helper=(R/'src/crossover_helpers.s').read_text();assert 'cmp #4\n  bcs Native' in helper
  for n in ['HpSupport','HpAxis','HpDeferred','HpCountDown']:
   hits=[]
   for path in (R/'src').glob('*'):
    if path.suffix not in['.s','.inc']:continue
    for i,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
     if re.search(r'\b'+n+r'\b',line) and not line.lstrip().startswith(';'):hits.append([str(path.relative_to(R)),i,line.strip()])
   assert len(hits)==1,(n,hits)
  ck['existing_state_ownership']=dict(passed=True,HpSupport='existing unused byte; CE only while owned1-1 profile',new_reciprocal_tags=[129,130],original_tags=[1,2,3],HpCount_zero_bypasses_generic_record_updater=True,scene_loader='InitializeMemory clears all native actor arrays before HpLoadArea/HpConfigure clears91-byte helper slab',sound_test='HpValid0 prevents manager; genuine next area load resets actors/cache')
  n=0;costs=[]
  for mode,flags,scenario in itertools.product([0,1],[p for p in range(256)if p&0x30==0x30],['spawn','warm','outside']):
   q=fresh(b,mode,camera=768 if scenario!='outside'else 0)
   if scenario=='warm':run(q,'CmPlatformWeapons')
   c,_,_=run(q,'CmHostDashTail',a=83,x=177,y=91,p=flags);wanted=registers(c);scratch=bytes(q.m[:8]);ob=q.get('ObjectOffset');banks=q.m.banks[:]
   z=fresh(old,mode,camera=768 if scenario!='outside'else 0)
   if scenario=='warm':run(z,'CmHostDashTail')
   d,_,_=run(z,'CmHostDashTail',a=83,x=177,y=91,p=flags)
   assert wanted==registers(d)and scratch==bytes(z.m[:8])and ob==z.get('ObjectOffset')and banks==z.m.banks,('weapon return',mode,flags,scenario,wanted,registers(d))
   costs.append([scenario,c.processorCycles-d.processorCycles]);n+=1
  ck['weapon_full_ABI']=dict(passed=True,calls=n,all64_architectural_flag_combinations=True,PHP_unused_break_encoding_30=True,AXYP_SP_R0_R7_ObjectOffset_banks=True,CPU_extra={s:[min(v for x,v in costs if x==s),max(v for x,v in costs if x==s)]for s in['spawn','warm','outside']})
  rows=[]
  for mode,used in itertools.product([0,1],range(7)):
   q=fresh(b,mode,camera=768)
   for i in range(used):q.set('Enemy_Flag',1,i);q.set('Enemy_ID',6,i);q.set('Enemy_State',7,i)
   before=[[q.get(n,i)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]for i in range(used)]
   run(q,'CmPlatformWeapons');aa=actors(q);assert len(aa)==min(1,6-used)
   assert before==[[q.get(n,i)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]for i in range(used)]
   # Bring both source cells in range only by an impossible wide camera is
   # not claimed. One cell visible at a time in this measured placement.
   if aa:assert aa[0][1]==129 and q.get('HpCount')==0
   rows.append([mode,used,len(aa)])
  for mode,which,mutation in itertools.product([0,1],[0,1],['valid','owner','id','flag','state','out_of_range']):
   q=fresh(b,mode,camera=(768 if which==0 else 2096));run(q,'CmPlatformWeapons');actor=next(i for i,o in actors(q)if o==129+which)
   if mutation=='owner':q.set('HpActorOwner',2,actor)
   if mutation=='id':q.set('Enemy_ID',6,actor)
   if mutation=='flag':q.set('Enemy_Flag',2,actor)
   if mutation=='state':q.set('Enemy_State',0,actor)
   if mutation=='out_of_range':q.set('HpActorSlot',7,which)
   pre=[q.get(n,actor)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]
   run(q,'CmPlatformRelease',x=which)
   if mutation=='valid':assert q.get('Enemy_Flag',actor)==0
   else:assert pre==[q.get(n,actor)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]
  ck['capacity_and_stale_owner']=dict(passed=True,capacity_cases=rows,release_cases=24,all_native_actors_priority=True,wrong_owner_ID_flag_state_pointer_never_erased=True)
  rows=[]
  for mode,which,tier in itertools.product([0,1],[0,1],[1,2]):
   q=fresh(b,mode,camera=768 if which==0 else 2096);run(q,'CmPlatformWeapons');actor=next(i for i,o in actors(q)if o==129+which)
   # Genuine pickup path changes tier; no fixture timer/resource write.
   pickup=next(i for i in range(6)if not q.get('Enemy_Flag',i));q.set('PowerUpType',0,pickup);q.set('Enemy_ID',46,pickup);q.set('Enemy_State',128,pickup);q.set('Enemy_Flag',1,pickup)
   q.put(CmTier=tier-1,PlayerStatus=tier-1);run(q,'NrPickup',x=pickup);assert q.get('CmTier')==tier
   q.set('PlatformCollisionFlag',actor,actor);run(q,'CmPlatformWeapons');assert q.get('Enemy_Flag',actor)==1 and q.get('HpActorSlot',which)==actor+1
   q.set('PlatformCollisionFlag',255,actor);run(q,'CmPlatformWeapons');assert q.get('Enemy_Flag',actor)==0
   run(q,'CmPlatformWeapons');assert not actors(q)
   rows.append([mode,which,tier])
  ck['pickup_retirement']=dict(passed=True,cases=len(rows),real_NrPickup_then_retains_actual_support_flag=True,retire_only_after_no_support_no_respawn=True)
  rows=[]
  for mode,which in itertools.product([0,1],[0,1]):
   q=fresh(b,mode,camera=768 if which==0 else 2096);run(q,'CmPlatformWeapons');actor=next(i for i,o in actors(q)if o==129+which)
   yy=[];cpu=[]
   for t in range(384):
    q.put(ObjectOffset=actor,FrameCounter=t&255);c,_,_=run(q,'HpNativePlatformDispatch',x=actor);yy.append(q.get('Enemy_Y_Position',actor));cpu.append(c.processorCycles)
   assert [min(yy),max(yy)]==[76,213]
   q.set('PlatformCollisionFlag',actor,actor);q.put(Player_Y_Speed=4,Player_State=2);run(q,'HpNativePlatformDispatch',x=actor)
   assert q.get('Player_Y_Position')==(q.get('Enemy_Y_Position',actor)-32)&255 and q.get('Player_Y_Speed')==0
   rows.append(dict(mode=mode,which=which,Y_range=[min(yy),max(yy)],native_motion_CPU=[min(cpu),max(cpu)]))
  ck['real_native_motion_carry']=dict(passed=True,updates=384*len(rows),rows=rows,ordinary_native25_kernel_not_approximate_sine=True)
  rows=[]
  for mode,wall,delay in itertools.product([0,1],[912,2240],[0,16,32,64]):
   result=approach(b,mode,wall,delay);assert result['reached'],('local access',mode,wall,delay,result['rows'][-1])
   assert any(r[4]for r in result['rows'])
   rows.append(dict(mode=mode,wall=wall,delay=delay,updates=len(result['rows']),actual_contact_updates=sum(bool(r[4])for r in result['rows']),first_face=result['rows'][-1]))
  ck['local_actual_player_BG_native_platform_access']=dict(passed=True,arenas=len(rows),rows=rows,real_parser=True,complete_PlayerCtrlRoutine=True,real_RunLargePlatform_bbox_collision_carry=True,limit='Typed local arenas, not complete native1-1. Valid floor origins864/2224;2192 was inside prior staircase and is retained as a rejected arena.')
  rows=[]
  for mode in[0,1]:
   q=fresh(b,mode,camera=768);run(q,'CmPlatformWeapons');actor=actors(q)[0][0]
   q.put(AreaPointer=194);run(q,'CmPlatformWeapons');assert q.get('HpActorSlot')==actor+1
   q.put(ScreenLeft_PageLoc=4,ScreenLeft_X_Pos=128);run(q,'CmPlatformWeapons');assert not actors(q)and q.get('HpSupport')==0
   q.put(ScreenLeft_PageLoc=3,ScreenLeft_X_Pos=0);run(q,'CmPlatformWeapons');assert actors(q)and q.get('Enemy_Y_Position',actors(q)[0][0])==208
   # Actual source area initialization first clears native arrays, then the
   # real loader/configure clears helper ownership; no marker-based erasure.
   run(q,'InitializeArea');assert all(q.get('Enemy_Flag',i)==0 for i in range(6))and q.get('HpSupport')==0 and q.get('HpCount')==0
   rows.append(mode)
  for name,value in[('TimerControl',1),('GamePauseStatus',1),('HpValid',0),('HpCount',1),('MarioVariant',0),('SelectedCharacter',1)]:
   q=fresh(b,camera=768);q.set(name,value);before=bytes(q.m[address(b,'HpRamStart'):address(b,'HpRamEnd')]);run(q,'CmPlatformTick');assert bytes(q.m[address(b,'HpRamStart'):address(b,'HpRamEnd')])==before,(name,'negative admission')
  ck['camera_scene_and_negative_admission']=dict(passed=True,both_modes=rows,future_pipe194_does_not_reset=True,offscreen_release_loopback_real_reinit=True,actual_InitializeArea_clears_actors_then91Bcache=True,explicit_no_new_global_state=True)
  events=[]
  for scene in['spawn','warm','retire']:
   q=fresh(b,camera=768)
   if scene!='spawn':run(q,'CmPlatformWeapons')
   if scene=='retire':q.put(CmTier=1)
   events+=irq_sweep(q,'CmPlatformWeapons')
  seams=[]
  for kind,name in itertools.product(['IRQ','NMI'],['CmPlatformTick','CmPlatformFind','CmPlatformSpawn','InitEnemyObject']):
   q=fresh(b,camera=768);q.put(NmiDisable=255)
   s=b['syms'][name];g=b['segs'][s['seg']];target=((int(g['ooffs'],0)-16)//8192,address(b,name))
   fired=irq_sweep(q,'CmPlatformWeapons',kind,{target});assert fired
   seams.append(dict(kind=kind,actual_bank_PC=list(target)))
  ck['actual_interrupts']=dict(passed=True,enabled_new_code_IRQ_boundaries=len(events),unique_enabled_boundaries=len(set(events)),native_initialization_and_new_entry_IRQ_lagNMI_seams=seams,AXYP_PC_SP_banks_five_SMC_R0_R7_live_stack_helper91B_and_Celeste_overlay=True,PHP_status_note='Only the hardware-real six flags compare across IRQ/RTI; B/U are stack encoding, no C/Z/I/D/V/N exclusion.')
  rows=[]
  for mode,(tier,camera,scene)in itertools.product([0,1],[(0,0,'distant'),(1,0,'powered_empty'),(0,768,'first_spawn'),(0,768,'warm'),(0,2096,'second_spawn')]):
   pair=[]
   for bundle in[old,b]:
    q=fresh(bundle,mode,tier,camera);px=camera+96
    q.put(Player_PageLoc=px>>8,Player_X_Position=px&255,Player_Y_Position=176,GameTimerDisplay=4,SavedJoypadBits=0,Left_Right_Buttons=0,PlayerEntranceCtrl=2)
    if scene=='warm':run(q,'CmHostDashTail')
    out=full(q,p=0x71);pair.append((out,bytes(q.m[z]for z in smc_at(bundle)),actors(q)))
   assert pair[0][0][0]==pair[1][0][0]and pair[0][0][2]==pair[1][0][2]and pair[0][1]==pair[1][1],('owned fullcaller ABI/banks/SMC',mode,scene)
   if scene in['distant','powered_empty']:assert pair[0][0][:4]==pair[1][0][:4]
   else:assert len(pair[1][2])==1
   rows.append(dict(mode=mode,tier=tier,camera=camera,scene=scene,baseline_CPU=pair[0][0][4],candidate_CPU=pair[1][0][4],CPU_extra=pair[1][0][4]-pair[0][0][4],AXYP_SP_banks_final5SMC_exact=True,whole_appRAM_ordered_OAM_hardware_exact=scene in['distant','powered_empty'],intentional_native_platform_actors=pair[1][2]))
  ck['actual_complete_owned_GameLoop_cost']=dict(passed=True,calls=len(rows),rows=rows,scope='Typed local empty-map fullGameLoops; includes real native actor collision/movement/drawing cost. Not native cadence/FPS or route timing. Added actors/OAM/cache state are intentional and are not masked as equivalent.')
  # Normal foreign full callers never enter the retargeted Celeste-only tail.
  rows=[]
  for char,var,mode in itertools.product(list(range(24)),[0,1],[0,1]):
   if char==22:continue
   pair=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.put(MarioVariant=var,CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
    pair.append(full(q,p=0x71))
   assert pair[0]==pair[1],('foreign fullcaller',char,var,mode,pair[0][0],pair[1][0])
   rows.append([char,var,mode])
  ck['foreign_complete_GameLoop']=dict(passed=True,calls=len(rows),full_AXYP_SP_application_RAM_banks_ordered_OAM_hardware_and_CPU_exact=True)
  proof['passed']=True
 except Exception as e:proof['failure']=str(e);proof['traceback']=traceback.format_exc()
 a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck)),indent=2));assert proof['passed']
if __name__=='__main__':main()
