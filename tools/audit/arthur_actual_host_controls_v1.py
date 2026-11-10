"""Real private cartridge CPU consumers. Isolated legal scenes, not native admission."""
from pathlib import Path
import argparse,hashlib,importlib.util,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];O=R/'build/arthur-host-integration-v1'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import dragon_power_gameplay_controls_v1 as C
import supermaaa_host_controls_v1 as M
from sunny_integrated_controls_v1 import registers,smc_at
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def point(b,n):return((location(b,n)-16)//8192,address(b,n))
def setup(b,ch=32):
 q=C.setup(b,ch)
 if ch==32:
  q.put(CurrentPlayer=0,NumberofLives=2,OffScr_NumberofLives=4)
  C.M.runtrace(q,'HuFresh')
 return q
def call(q,n,**kw):return C.M.runtrace(q,n,**kw)
def exact_maps(q):
 assert q.get('CurrentBank')&127==q.m.banks[1]
 assert q.get('CurrentBankC')&127==q.m.banks[2]
def owned(q,name,**kw):
 pc=address(q.b,name);q.put(ArDrawPtr=pc&255);q.set('ArDrawPtr',pc>>8,1)
 c,tr,mn=call(q,'ArDispatch',**kw);assert point(q.b,name)in tr,(name,'not reached')
 exact_maps(q);return c,tr,mn
def lifecycle(b):
 q=setup(b);assert q.get('ArR_053A')==64
 owned(q,'ArHostNativePickup',a=6);assert q.get('ArR_053A')==68
 # Real injury/source-state entry, then persist through a genuine scene key.
 owned(q,'ArTakeHit');assert q.get('ArR_04F0')&32
 owned(q,'ArHostSave');assert q.get('ArProfileWeapon')==68 and q.get('ArProfileFlags')==32
 rows=[]
 for n,v in [('AreaNumber',1),('WorldNumber',2),('AreaAddrsLOffset',7)]:
  q.set(n,v);call(q,'HuReset');assert q.get('ArR_053A')==68 and q.get('ArR_04F0')&32
  rows.append([n,v,q.get('ArHostPhase'),q.get('ArHostReady')])
 # Existing native seven-byte player transpose really runs. The installed
 # menu remains one-player; this fixture explicitly enables the optional path.
 q.put(NumberOfPlayers=1,OffScr_NumberofLives=4,OffScr_AreaNumber=3,OffScr_WorldNumber=1)
 for turn in range(4):
  if turn==2:q.put(NumberofLives=1)
  call(q,'NativeRareTransposePlayersCore');call(q,'HuGraphics')
  want=[64,68,66,64][turn]
  # Player1 acquires dagger before returning to player0.
  assert q.get('ArR_053A')==want,(turn,'player weapon',q.get('ArR_053A'),want)
  if turn==0:owned(q,'ArHostNativePickup',a=8);owned(q,'ArHostSave')
  rows.append(['transpose',turn,q.get('CurrentPlayer'),q.get('ArR_053A'),q.get('ArR_04F0')&32])
 # Actual generic global reset must precede the final selected-owner init.
 call(q,'X5ProfilesNewGame');assert not any(q.m[0x5f90:0x5f98])
 call(q,'HuFresh');assert q.get('ArR_053A')==64 and q.get('ArHostReady')==167
 return dict(actual_native_transposes=4,scene_and_newgame_rows=rows,optional_two_player_fixture_disclosed=True)
def interrupts(b):
 spec=importlib.util.spec_from_file_location('arthur_actual_nmi',R/'build/character-host-union-v5/gm_verify_nmi.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);g.B=b
 rows=[];q=setup(b);q.put(DisableScreenFlag=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
 for lag,pause in itertools.product([0,255],[0,1]):
  q.put(NmiDisable=lag,GamePauseStatus=pause,ArHostPhase=1,ArHostDue=0)
  q.m.writes=[];z=g.nmi(q)
  clock=(address(b,'ArHostNmiClock')-8192,63)
  assert z['trace'].count(clock)==1,('exact source clock once',lag,pause)
  assert q.get('ArHostPhase')==(1 if pause else 3)and q.get('ArHostDue')==int(not pause)
  palette=(address(b,'ArHostNmiPalette')-8192,70)
  assert z['trace'].count(palette)==int(lag==0),('palette normal-only',lag,pause)
  if lag==0:
   ppu=[(a,v)for a,v in q.m.writes if a in [0x2006,0x2007]]
   assert ppu[-5:]==[(8198,63),(8198,17),(8199,54),(8199,24),(8199,18)],('actual normal palette',ppu[-10:])
   scroll=[v for a,v in q.m.writes if a==0x2005];assert scroll[-2:]==[0,0]and len(scroll)>=4,('actual palette scroll restore',scroll)
   done=(address(b,'ArPaletteScrollDone'),117);assert z['trace'].count(done)==1
  else:assert(address(b,'ArPaletteScrollDone'),117)not in z['trace'],('lag must keep published PPU frame')
  rows.append(dict(lag=lag,pause=pause,**g.scheduler.summary(z)))
 q.put(GamePauseStatus=0,NmiDisable=255,ArHostPhase=1,ArHostDue=0);call(q,'AudioUpdate')
 assert q.get('ArHostPhase')==1 and q.get('ArHostDue')==0,('ordinary Main audio ticks source clock')
 seams=[]
 for n in ['ArDispatch','ArHostMovement','ArStep','ArHostAfterTerrain','ArHostGraphics','ArHostDraw']:
  q=setup(b);q.put(DisableScreenFlag=1,ArHostDue=1,ArHostPad=129,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
  bank,pc=point(b,n);c,z=g.scheduler.invoke(q.m,'GameLoop',sp=240,cut=(pc,bank,'NMI'))
  exact_maps(q);assert q.get('ArHostReady')==167
  seams.append(dict(entry=n,**g.scheduler.summary(z),ISR=g.scheduler.summary(z['interrupt'])))
 return dict(actual_normal_lag_vectors=rows,ordinary_Main_audio_no_clock=True,in_flight_Main_seams=seams,scope='Real vectors/mapper/AXYP/SP/liveZP/33SMC; no PPU DMA stealing or hardware deadline claim.')
def pickups(b):
 rows=[]
 for slot,kind,mature in itertools.product(range(6),range(2),[False,True]):
  q=setup(b);owned(q,'ArTakeHit');before=q.get('ArR_04F0')
  C.actor(q,slot,0x2e,96,176);q.set('PowerUpType',kind,slot);q.set('Enemy_State',128 if mature else 0,slot)
  call(q,'NrPrepare',x=slot);c,tr,mn=call(q,'NrPickup',x=slot,p=0x71)
  if mature:
   assert q.get('Enemy_Flag',slot)==0 and point(b,'EraseEnemyObject')in tr
   assert q.get('FloateyNum_Control',slot)==6
   if kind==0:assert not q.get('ArR_04F0')&32
   else:assert q.get('ArR_053A')==68
  else:assert q.get('ArR_04F0')==before and q.get('Enemy_Flag',slot)==1
  rows.append([slot,kind,mature,c.processorCycles,mn])
 weaponrows=[]
 for cycle,want,handler in [(0,64,'ArNativeLance'),(1,68,'ArNativeTorch'),(2,54,'ArNativeAxe'),(3,66,'ArNativeDagger'),(4,79,'ArNativeCross')]:
  q=setup(b)
  for _ in range(cycle):
   C.actor(q,5,0x2e,96,176);q.set('PowerUpType',1,5);q.set('Enemy_State',128,5);call(q,'NrPickup',x=5)
  assert q.get('ArR_053A')==want
  seen=set();active=False
  for age in range(54):
   keys=64 if age%18==0 else 0
   q.put(SavedJoypadBits=keys,ArHostPad=keys,ArHostDue=int(age%3==0),VRAM_Buffer1_Offset=0,NmiDisable=255)
   c,tr,mn=call(q,'GameLoop');seen.update(tr)
   active=active or any(q.get('ArR_04F0',i)&128 for i in [1,2,3])
  assert active and point(b,handler)in seen,(want,'actual B source weapon consumer missing',active,handler)
  weaponrows.append([want,handler,active])
 return dict(actual_native_mature_pickup_cases=rows,actual_Main_B_driven_five_weapon_handlers=weaponrows,scope='Isolated legal native pickup scenes/source-clock boundary; earned world route still pending.')

def powerup_chooser(b):
 # Execute the real block emitter and its native status-dependent chooser.
 # Only the emergence maturity is supplied at this isolated scene boundary;
 # PowerUpType is never forced to the expected mushroom/flower result.
 rows=[]
 def emit(q,slot):
  call(q,'HuGraphics')
  q.put(SprDataOffset_Ctrl=0,VRAM_Buffer1_Offset=0)
  q.set('Block_PageLoc',1);q.set('Block_X_Position',128);q.set('Block_Y_Position',160)
  q.set('PowerUpType',0,slot) # native question-block generic mushroom/flower request
  c,tr,mn=call(q,'SetupPowerUp',x=slot)
  assert point(b,'UnionPwrUpCore')in tr and point(b,'RlPrepareDispatch')in tr
  assert q.get('Enemy_ID',slot)==46 and q.get('Enemy_State',slot)==1 and q.get('Enemy_Flag',slot)==1
  assert q.get('Enemy_X_Position',slot)==128 and q.get('Enemy_Y_Position',slot)==152
  return q.get('PowerUpType',slot),c.processorCycles
 for slot in range(6):
  q=setup(b)
  kind,cost=emit(q,slot);assert kind==1 and q.get('PlayerStatus')==1,('armored Arthur must reveal Flower',slot)
  owned(q,'ArTakeHit')
  kind,cost=emit(q,slot);assert kind==0 and q.get('PlayerStatus')==0,('naked Arthur must reveal repair Mushroom',slot)
  q.set('Enemy_State',128,slot);call(q,'NrPickup',x=slot)
  assert not q.get('ArR_04F0')&32 and q.get('Enemy_Flag',slot)==0
  sequence=[]
  for want in [68,54,66,79,64]:
   kind,cost=emit(q,slot);assert kind==1 and q.get('PlayerStatus')==1,('repaired Arthur must reveal Flower',slot)
   q.set('Enemy_State',128,slot);call(q,'NrPickup',x=slot)
   assert q.get('ArR_053A')==want and q.get('Enemy_Flag',slot)==0,('actual revealed Flower did not cycle source weapon',slot,want)
   sequence.append(want)
  rows.append(dict(slot=slot,armored_reveal=1,naked_reveal=0,post_repair_source_weapon_sequence=sequence,emitter_cycles=cost))
 return dict(actual_block_emission_cases=42,rows=rows,native_emergence_maturity_fixture=True,scope='Real SetupPowerUp/UnionPwrUpCore and native pickup dispatch; controller-earned world route remains pending.')
def portrait(b):
 q=C.setup(b,23);q.put(CrossoverMenuIndex=31,OperMode=0,CrossoverMenuState=2,VRAM_Buffer1_Offset=0)
 call(q,'HuResolve');assert q.get('SelectedCharacter')==32 and q.get('ArHostReady')==167
 c,tr,mn=call(q,'QueueSelection');assert point(b,'FmDrawPreview')in tr
 assert[q.get('CurrentCHRBank',i)for i in range(4)]==[188,189,190,191]
 assert[q.get('X5ChrMode',i)for i in range(4)]==[130]*4
 # Scene reset restores all eight native windows before the real lives draw.
 q.put(OperMode=1,GameEngineSubroutine=0,CurrentOAMOffset=0);call(q,'HuReset')
 before=[q.get('CurrentCHRBank',i)for i in range(8)]
 call(q,'DrawPlayer_Intermediate');c,tr,mn=call(q,'X5PortraitRender')
 assert point(b,'ArHostPortrait')in tr
 assert q.get('CurrentOAMOffset')>0
 assert[q.get('CurrentCHRBank',i)for i in range(1,8)]==before[1:],('cold portrait overwrote world windows')
 assert q.get('ObjectMetasprite')==address(b,'METASPRITE_SAMUS_BODY')
 assert q.get('CurrentBankC')&127==q.m.banks[2]==88,('cold graphics bank fell through raw32 table',q.m.banks)
 return dict(menu_selected_raw32=True,approved_menu_art_index=30,lives_parts=q.get('CurrentOAMOffset')//4,lives_common_windows_preserved=True,live_register_mapper_restoration=True)
def presentation(b):
 rows=[]
 for area,bg in itertools.product(range(4),[0,4,5,7]):
  q=setup(b);q.put(AreaType=area,BackgroundColorCtrl=bg,VRAM_Buffer1_Offset=0)
  c,tr,mn=call(q,'GetPlayerColors');assert point(b,'ArHostColors')in tr and point(b,'X5QueueAreaBackdrop')in tr
  expected=[34,34,15,15,15,34,15,15][bg or area]
  at=address(b,'VRAM_Buffer1');assert list(q.m[at:at+5])==[63,16,1,expected,0]
  rows.append([area,bg,expected])
 q=setup(b);q.put(VRAM_Buffer1_Offset=0);c,tr,mn=call(q,'HuStatus',a=0,y=55)
 assert list(q.m[address(b,'VRAM_Buffer1')+11:address(b,'VRAM_Buffer1')+18])==[10,27,29,17,30,27,36]
 assert c.a==0 and c.y==55
 return dict(actual_native_backdrop_cases=rows,native_seven_cell_status_name='ARTHUR ',opaque_source_black_remains_in_world_P3_index1=True)
def render_pixels(b):
 spec=importlib.util.spec_from_file_location('arthur_source_raster',R/'tools/audit/arthur_coalesced_palette_v1.py');raster=importlib.util.module_from_spec(spec);spec.loader.exec_module(raster)
 spec=importlib.util.spec_from_file_location('arthur_pixel_nmi',R/'build/character-host-union-v5/gm_verify_nmi.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 source=json.loads((R/'build/arthur-source-v1/art-source.json').read_text());records={v['pose']:v for v in source['records']}
 sourcechr=(R/'build/arthur-source-v1/arthur-original-sprites.chr').read_bytes();sourcepal=source['palette']['hardware_indices'][16:32]
 poses=json.loads((R/'build/arthur-palette-leaf-v6/atlas-proof.json').read_text())['posemap']
 roles=json.loads((R/'build/arthur-palette-role-controls-v1/roles.json').read_text())['roles']
 nes=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();rgb=lambda c:tuple(nes[c*3:c*3+3])
 count=0;maxparts=0;opaque_black=0
 for pose,mode in itertools.product(map(int,poses),range(3)):
  q=setup(b);area=1 if mode==0 else 3
  q.put(Player_X_Position=96,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=1,
    AreaType=area,SmFreezePaletteControl=8 if mode==2 else area+1,CurrentOAMOffset=0,GuestOamRotationActive=0,DisableScreenFlag=1)
  owned(q,'ArHostImport');owned(q,'ArHostPaletteMode')
  # Actual native full area packet, optionally followed by the real Bowser
  # palette replacement, then Arthur's true normal-NMI palette publisher.
  palette=[0]*32
  for ctrl in [area+1]+([8]if mode==2 else []):
   q.put(NmiDisable=0,VRAM_Buffer_AddrCtrl=ctrl,VRAM_Buffer1_Offset=0);q.m.writes=[];g.nmi(q)
   addr=0;toggle=0;ppu_ctrl=0
   for a,v in q.m.writes:
    if a==0x2000:ppu_ctrl=v
    elif a==0x2006:
     if toggle==0:addr=(v&63)<<8;toggle=1
     else:addr=(addr&0x3f00)|v;toggle=0
    elif a==0x2007:
     if addr&0x3f00==0x3f00:
      ix=addr&31
      if ix in [16,20,24,28]:ix-=16
      palette[ix]=v&63
      if ix in [0,4,8,12]:palette[ix+16]=v&63
     addr=(addr+(32 if ppu_ctrl&4 else 1))&0x3fff
  slot=0 if pose<54 else 1
  for i in range(4):q.set('ArR_04F0',128 if i==slot else 0,i)
  for n,v in [('ArR_0522',pose),('ArR_05AF',104),('ArR_0583',1),('ArR_0599',200),('ArR_056D',0)]:q.set(n,v,slot)
  q.m[0x200:0x300]=[248,0,0,0]*64
  owned(q,'ArHostDraw');actual={};parts=q.get('CurrentOAMOffset')//4;maxparts=max(parts,maxparts)
  for i in range(parts):
   y,tile,attr,x=q.m[512+i*4:516+i*4];window=(tile&1)*4+(tile>>6)
   page=q.get('CurrentCHRBank',window)+(q.get('X5ChrMode',window)&3)*256
   assert 868<=page<881,('actual pixel pattern publisher',pose,mode,page)
   at=16+128*8192+page*1024+(tile&62)*16;pat=b['raw'][at:at+32]
   for dy,dx in itertools.product(range(16),range(8)):
    sy=15-dy if attr&128 else dy;sx=7-dx if attr&64 else dx;v=(pat[sy//8*16+sy%8]>>(7-sx)&1)|((pat[sy//8*16+sy%8+8]>>(7-sx)&1)<<1)
    if v:actual.setdefault((x+dx,y+dy),(rgb(palette[16+(attr&3)*4+v]),attr&32))
  rows={p:8 for p in range(22)}|{p:2 for p in range(32,54)}|{22:2,24:1,26:1}
  row=rows[pose]if pose<54 else next(v['source_row']for v in roles if v['family']=='weapons'and v['pose']==pose)if pose not in [86,102,248,249]else 0
  src=raster.raster(records[pose],row,sourcechr,sourcepal)
  expected={(x+104,y+200):(rgb(c),priority)for(x,y),(c,priority)in src.items()}
  assert actual==expected,('actual cartridge source RGB/alpha/priority',pose,mode,len(actual),len(expected),list(set(actual.items())^set(expected.items()))[:4],palette,q.get('ArHostOldPage'),list(q.m[512:512+parts*4]))
  opaque_black+=sum(c==15 for c,priority in src.values());count+=1
 return dict(actual_cartridge_pose_area_cases=count,all_source_pixels_alpha_priority_exact=True,opaque_original_black_pixels_checked=opaque_black,max_body_or_weapon_OAM_parts=maxparts,source_20_30_white_RGB_alias_explicit=True,actual_normal_NMI_palette_and_Bowser_packets=True)
def foreign_nmi(b):
 spec=importlib.util.spec_from_file_location('arthur_foreign_nmi',R/'build/character-host-union-v5/gm_verify_nmi.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 old=scoped_load(R/'build/ice-pose-aliases-v2/candidate.nes');rows=[]
 for ch,lag in itertools.product([0,1,2,3,4,5,6,7,9,13,15,18,19,20,21,23,24,26,28],[0,255]):
  pair=[]
  for v in [old,b]:
   q=C.setup(v,ch);q.put(NmiDisable=lag,DisableScreenFlag=1,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0);q.m.writes=[]
   z=g.nmi(q);pair.append((q,z))
  (qa,za),(qb,zb)=pair
  assert C.M.fastapp(qa)==C.M.fastapp(qb),('foreign NMI application',ch,lag,M.different(C.M.fastapp(qa),C.M.fastapp(qb)))
  assert qa.m.banks==qb.m.banks
  def writes(q):return[(a,v)for a,v in q.m.writes if not 256<=a<512 and not 0x5114<=a<=0x5117]
  assert writes(qa)==writes(qb),('foreign NMI ordered nonstack/nonmapper writes',ch,lag)
  rows.append([ch,lag,zb['CPU']-za['CPU'],sum(a==0x5116 for a,v in qb.m.writes)-sum(a==0x5116 for a,v in qa.m.writes)])
 return dict(cases=len(rows),CPU_delta=[min(r[2]for r in rows),max(r[2]for r in rows)],rows=rows,declared_gateway_C_window_maps_are_extra=True)
def cold_packets(b):
 spec=importlib.util.spec_from_file_location('arthur_cold_packets',R/'build/character-host-union-v5/gm_verify_nmi.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 old=scoped_load(R/'build/ice-pose-aliases-v2/candidate.nes');rows=[]
 for ctrl,ch,capture in [(i,0,0)for i in range(20)]+[(0,18,1),(1,18,1),(2,18,1)]:
  pair=[]
  for v in [old,b]:
   q=C.setup(v,ch);q.put(OperMode=0 if ch==0 else 1,OperMode_Task=1,VRAM_Buffer_AddrCtrl=ctrl,DisableScreenFlag=1,NmiDisable=0,VRAM_Buffer1_Offset=0,VvVariant=capture,PnBombCapturePending=capture)
   q.m.writes=[];z=g.nmi(q);pair.append((q,z))
  (qa,za),(qb,zb)=pair
  def writes(q):return[(a,v)for a,v in q.m.writes if not 256<=a<512 and not 0x5114<=a<=0x5117]
  assert writes(qa)==writes(qb),('real VRAM packet writes',ctrl,ch,capture)
  assert C.M.fastapp(qa)==C.M.fastapp(qb),('real VRAM packet app',ctrl,ch,capture,M.different(C.M.fastapp(qa),C.M.fastapp(qb)))
  assert qa.m.banks==qb.m.banks
  rows.append([ctrl,ch,capture,len(writes(qb)),zb['CPU']-za['CPU']])
 for n in ['PnPaletteScreenUpdate','ArPnAfterPalette','PnHudPreUpdateScreen','FastNmiVramCopy']:
  assert point(b,n)==point(old,'PnPaletteScreenUpdate::Samus'if n=='ArPnAfterPalette'else n),(n,'fixed PN seam moved')
 return dict(actual_packet_forms=20,actual_Parodius_capture_forms=3,rows=rows,all_nonmapper_writes_application_final_maps_exact=True,limits='Real CPU VRAM packets, no hardware PPUDATA buffered palette-read model.')
def selectors(b):
 entries=['NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury','NrLegacyInjuryStatus','NrDeathStart','NrDeath','NrVisible','NrHead']
 targets=['ArHostMovement','ArHostGraphics','ArHostDraw','ArHostGraphics','ArHostShotContacts','ArHostInjury','ArHostStatus','ArHostDeath','ArHostNativeDeath','ArHostVisible','ArHostHead']
 rows=[]
 for n,t in zip(entries,targets):
  q=setup(b);q.put(CurrentOAMOffset=0)
  c,tr,mn=call(q,n,a=91,x=0,y=55,p=0x71)
  assert point(b,t)in tr,(n,'actual Arthur target not reached',t)
  exact_maps(q);rows.append([n,t,c.processorCycles,mn])
 return dict(cases=len(rows),rows=rows)
def mainloop(b):
 rows=[]
 for mode,face,skip in itertools.product(range(2),[1,2],[0,1]):
  q=setup(b);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,ShouldSkipDrawSprites=skip)
  costs=[];xs=[];ys=[];seen=set();minimum=253
  for age in range(48):
   # NMI clock supplies source input/tick due. This isolated phase fixture
   # sets only that boundary, never an intended movement or collision result.
   keys=(1 if face==1 else 2)|(128 if age in [6,16]else 0)|(64 if age in [24,36]else 0)
   q.put(SavedJoypadBits=keys,SavedJoypad1Bits=keys,ArHostPad=keys,ArHostDue=int(age%3==0),NmiDisable=255,VRAM_Buffer1_Offset=0)
   c,tr,mn=call(q,'GameLoop');costs.append(c.processorCycles);minimum=min(mn,minimum);seen.update(tr)
   assert q.get('SelectedCharacter')==32 and q.get('ArHostReady')==167,('Main owner overlay corrupted',mode,face,skip,age,q.get('ArHostReady'))
   assert point(b,'KbDrawShots')not in tr,('foreign Kirby consumer',age)
   assert point(b,'ArHostMovement')in tr,('missing source movement',age)
   assert q.get('ArHostDue')in [0,1]and q.get('ArHostPhase')in [1,2,3],('source clock corrupt',age)
   exact_maps(q);xs.append(q.get('Player_X_Position')+256*q.get('Player_PageLoc'));ys.append(q.get('Player_Y_Position'))
  assert max(xs)>min(xs),(mode,face,skip,'no source motion',xs)
  rows.append(dict(mode=mode,face=face,skip=skip,cycles=[min(costs),max(costs)],minimum_SP=minimum,X=xs,Y=ys,actual_source_draw=point(b,'ArHostDraw')in seen))
 return dict(updates=48*len(rows),rows=rows,scope='Actual complete GameLoop; isolated source-clock boundary supplied, not video cadence/controller proof.')
def foreign(b):
 old=scoped_load(R/'build/ice-pose-aliases-v2/candidate.nes')
 rows=[]
 for ch,mode,keys in itertools.product([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,26,28],range(2),[0,129]):
  pair=[]
  for v in [old,b]:
   q=C.setup(v,ch)
   if ch==28:call(q,'DkConstruct')
   q.put(CrossoverBehaviorVersion=mode,SavedJoypadBits=keys)
   c,tr,mn,ann,events=M.run_linked(q,'GameLoop',p=0x71)
   pair.append((q,c,tr,mn,ann,events))
  qa,ca,ta,ma,ana,ea=pair[0];qb,cb,tb,mb,anb,eb=pair[1]
  assert registers(ca)==registers(cb),('foreign AXYP/SP',ch,mode,keys,registers(ca),registers(cb))
  assert C.M.fastapp(qa)==C.M.fastapp(qb),('foreign application',ch,mode,keys,M.different(C.M.fastapp(qa),C.M.fastapp(qb)))
  assert qa.m.banks==qb.m.banks,('foreign maps',ch)
  assert[z[-1]for z in ea]==[z[-1]for z in eb],('foreign actual JumpEngine consumers',ch)
  def writes(q,bundle,ann):
   return[(a,ann.get(i,v))for i,(a,v)in enumerate(q.m.writes)if not 256<=a<512 and not 0x5114<=a<=0x5117 and a not in smc_at(bundle)and a not in[address(bundle,'CurrentBank'),address(bundle,'CurrentBankC')]]
  assert writes(qa,old,ana)==writes(qb,b,anb),('foreign ordered writes',ch,mode,keys)
  rows.append([ch,mode,keys,cb.processorCycles-ca.processorCycles,min(ma,mb)])
 return dict(cases=len(rows),CPU_delta=[min(r[-2]for r in rows),max(r[-2]for r in rows)],rows=rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--only',default='selectors,mainloop,foreign');a=ap.parse_args();assert not a.output.exists()
 b=scoped_load(O/'candidate.nes');d=dict(passed=False,native_run=False,checks={})
 try:
  for n in a.only.split(','):d['checks'][n]=globals()[n](b)
  d['passed']=True
 except Exception as e:d.update(failure=repr(e),traceback=traceback.format_exc())
 d['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',R/'build/ice-pose-aliases-v2/candidate.nes']}
 a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(passed=d['passed'],failure=d.get('failure'),checks=list(d['checks']))));assert d['passed']
if __name__=='__main__':main()
