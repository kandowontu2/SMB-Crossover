"""Bounded full-caller body/geometry controls. No native emulator/pixel claim."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_host_pipeline_controls_v1 as pipe
import rogue_dawn_map_v1 as ref
import prepare_rogue_dawn_art_v1 as art
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from sunny_integrated_controls_v1 import seed,run,app,registers,cleanwrites
O=R/'build/rogue-dawn-host-body-v1';P=R/'build/roster-shared-celeste-small-chr-v1.nes'
d=pipe.d
FLAGS=[0x30,0x31,0x70,0x71,0x34,0xf3]

def get(m,n,i=0):return m[address(m.bundle,n)+i]
def put(m,**kw):
 for n,v in kw.items():m[address(m.bundle,n)]=v
def context(m):return bytes(m[0x5c00:0x5c80])
def vis(m):
 # An explicit current-unit precondition. Future typed injury/visibility gate
 # must remove dependency on stale GuestHurt/Injury/MMdeath before admission.
 for n in ['GuestHurtKind','InjuryTimer','MmDeathFlag','GuestPowerupActive']:
  if n in m.bundle['syms']:m[address(m.bundle,n)]=0
def bbox(m):return list(m[address(m.bundle,'BoundingBox_UL_XPos'):address(m.bundle,'BoundingBox_UL_XPos')+4])
def expectbox(m):
 x=(get(m,'Player_X_Position')-get(m,'ScreenLeft_X_Pos')+8)&255;y=get(m,'Player_Y_Position')+16
 return[(x-m[0x5c02])&255,(y-m[0x5c01])&255,(x+m[0x5c02])&255,(y+m[0x5c01]+1)&255]
def snapshot(m,c):
 # Explicit dead stack and 5SMC only: never a broad application-RAM waiver.
 class Q:pass
 q=Q();q.b=m.bundle;q.m=m
 return registers(c),app(q),tuple(m.banks)

def draw(m,frame,face,offset=0,all_objects=False):
 b=m.bundle;m[0x5c03]=frame;m[0x5c2c]=face;vis(m)
 put(m,PlayerFacingDir=face+1,Player_SprAttrib=0,CurrentOAMOffset=offset,Player_X_Position=120,Player_Y_Position=144,Player_PageLoc=0,ScreenLeft_X_Pos=0,Player_Y_HighPos=1,DisableScreenFlag=0)
 for i in range(0,256,4):m[address(b,'Sprite_Data')+i]=248
 d.call(m,'PlayerGfxHandler',sp=240)
 before=context(m);consumed=[];oldstep=NesMPU.step
 def step(c):
  bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if c.pc==address(b,'HpNativePointerEnd') and bank==4 and c.y==0:
   ptr=m[address(b,'R0')]|m[address(b,'R1')]<<8
   consumed.append(dict(C=m.banks[2],pointer=ptr,header=m[ptr],SP=c.sp))
  oldstep(c)
 NesMPU.step=step
 try:
  if all_objects:
   # Real GameCoreRoutine predecessor reserves native player's56B before
   # actors draw. Cursor0 here would falsely let final tail-clear hide body.
   res,_,_=d.call(m,'PlayerOAMReservation',sp=240)
   put(m,CurrentOAMOffset=res.a)
   d.call(m,'DrawAllMetasprites',sp=240)
  else:
   # This is the real complete pointer-snapshot/legacy selector predecessor.
   d.call(m,'HpGraphicsBankCopy',sp=240)
   c,low,tr=d.call(m,'DrawMetasprite',x=get(m,'ObjectMetasprite'),y=0,sp=240)
 finally:NesMPU.step=oldstep
 assert before==context(m),'render cannot advance original action/animation'
 return consumed

def decoded_body(m,frame,face,start=0):
 b=m.bundle;ptr=get(m,'SmPosePtr')+256*get(m,'SmPosePtr',1)
 raw=b['raw'];at=16+94*8192+ptr-0xc000;rec=raw[at:at+1+raw[at]]
 if len(rec)==1:return {},rec
 # Genuine body records/OAM tiles; every emitted descriptor part must be
 # present in real renderer output at the exact source-derived coordinates.
 oam=bytes(m[address(b,'Sprite_Data'):address(b,'Sprite_Data')+256]);parts=[]
 for i in range(1,len(rec),4):
  tile,attr,y,x=rec[i:i+4];sx=x-256 if x&128 else x;sy=y-256 if y&128 else y
  want=bytes([(144+sy)&255,tile,attr,(120+sx)&255])
  matches=[j for j in range(0,256,4)if oam[j:j+4]==want]
  assert matches,('missing exact body OAM part',frame,face,list(want),list(oam[:80]),rec.hex())
  parts.append(list(want))
 first=680+(get(m,'SmChrBank')-168)
 base=16+1048576+first*1024;pixels={}
 for y,t,attr,x in reversed(parts):
  tile=t&254
  for yy in range(16):
   sy=15-yy if attr&128 else yy
   for xx in range(8):
    sx=7-xx if attr&64 else xx;z=base+tile*16+(sy//8)*16+sy%8
    v=((raw[z]>>(7-sx))&1)|(((raw[z+8]>>(7-sx))&1)<<1)
    if v:pixels[x-128+xx,y+1-160+yy]=(v,attr&0x23)
 return pixels,rec

def main():
 b=d.old.scoped_load(O/'candidate.nes');parent=d.old.scoped_load(P);proof=dict(passed=False,native_run=False,source_CPU_only=True,ROM_sha256=ref.digest((O/'candidate.nes').read_bytes()),checks={});checks=proof['checks'];minimum=255
 try:
  # Exact contact geometry and native-clamped source center, every admitted
  # source radius class and both viewport/page edges. No legacy SmBall read.
  rows=[]
  for ry,rx,wx,y,camera in itertools.product([8,15,4],[4,7,16],[8,120,252,260],[32,144,176,215],[0,7]):
   m=pipe.base(b);m[0x5c01],m[0x5c02]=ry,rx;put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,Player_Y_Position=y,ScreenLeft_X_Pos=camera)
   c,l,tr=d.call(m,'RdBodyBox');minimum=min(minimum,l)
   assert bbox(m)==expectbox(m) and m[0x5c0d]==(y+16)&255
   assert m[0x5c0c]*256+m[0x5c0e]==wx+8
   assert address(b,'SmBall')not in m.reads
   rows.append(dict(radius=[ry,rx],worldX=wx,y=y,camera=camera,box=bbox(m),CPU=c.processorCycles))
  checks['source_radii_committed_native_box']=rows
  # Actual old copied post-BG owner no longer rewrites exact Rogue source box,
  # including intentionally stale old SmCeilingHit; foreign is literal tail.
  rows=[]
  for char,var,p in itertools.product([0,1,2,3,4,21,23,255],[0,1,2],FLAGS):
   if(char,var)==(2,1):
    m=pipe.base(b);put(m,SmCeilingHit=1);before=context(m);c,l,tr=d.call(m,'Z2PostBGBodyBridge',a=91,x=4,y=7,p=p,sp=224)
    assert(c.a,c.x,c.y,c.p&207)==(91,4,7,p&207)and before==context(m)
   else:
    pair=[]
    for bundle in[parent,b]:
     m=d.old.make(bundle);put(m,SelectedCharacter=char,SmCeilingHit=1);m[0x5fee]=var
     c,l,tr=d.call(m,'Z2PostBGBodyBridge',a=91,x=4,y=7,p=p,sp=224);pair.append(snapshot(m,c)+(c.processorCycles,))
    assert pair[0][:3]==pair[1][:3],('foreign postBG',char,var,p)
    rows.append(pair[1][3]-pair[0][3])
  checks['inline_postBG_exact_foreign']=dict(cases=len(rows),CPU_delta=sorted(set(rows)),owned_preserves_AXYP_XY_and_source=True)
  # Genuine H/V/small-platform callers, all forms, both horizontal carries,
  # actor slots0/4, low-byte page edges, and high-byte platform top borrow.
  rows=[]
  for ry,face,owner,slot,top,delta,wx in itertools.product([8,15,4],[0,1],['PositionPlayerOnHPlat','PositionPlayerOnVPlat','PositionPlayerOnS_Plat'],[0,4],[16,64,176],[0,1,255],[0,255,256]):
   if owner=='PositionPlayerOnS_Plat'and delta!=0:continue
   m=pipe.base(b);m[0x5c01],m[0x5c02],m[0x5c2c]=ry,4,face
   put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8)
   m[address(b,'Enemy_Y_Position')+slot]=top;m[address(b,'Enemy_Y_HighPos')+slot]=1;m[address(b,'Enemy_ID')+slot]=40;m[address(b,'R0')]=delta
   c,l,tr=d.call(m,owner,a=2 if owner=='PositionPlayerOnS_Plat'else top,x=slot,sp=224);minimum=min(minimum,l)
   assert get(m,'Player_Y_Position')==(top-ry-17)&255,(ry,owner,top,get(m,'Player_Y_Position'))
   assert get(m,'Player_Y_HighPos')==(1 if top>=ry+17 else 0)
   assert m[0x5c0d]==(top-ry-1)&255 and get(m,'Player_Y_Speed')==m[0x5c08]==m[0x5c14]==0 and m[0x5c2d]==1
   assert m[0x5c0c]*256+m[0x5c0e]==(get(m,'Player_PageLoc')*256+get(m,'Player_X_Position')+8)&65535
   assert bbox(m)==expectbox(m)
   rows.append(dict(radiusY=ry,facing=face,caller=owner,slot=slot,top=top,delta=delta,worldX=wx,CPU=c.processorCycles,minimum_SP=l))
  checks['actual_platform_landing_and_carry_all_forms']=rows
  # Body-only CHR/publication and exact source colors: complete suit/missile
  # requests, busy packet retry, no backdrop/enemy/effect windows rewritten.
  rows=[]
  for suit,missile,offset,shadow,p in itertools.product([0,32],[0,1],[0,7,77,78,83],[168,169],FLAGS[:2]):
   m=pipe.base(b);m[0x5fb0]=suit;m[0x5c7c]=1;m[0x5c3d]=missile
   # Use genuine symbol, not assumed raw missile field.
   m[address(b,'RdMissileMode')]=missile
   for i in range(12):m[address(b,'CurrentCHRBank')+i]=(shadow+i)&255;m[address(b,'X5ChrMode')+i]=i+3
   put(m,VRAM_Buffer1_Offset=offset,SmChrBank=168)
   for i in range(84):m[address(b,'VRAM_Buffer1')+i]=(i*17+29)&255
   before=bytes(m[address(b,'CurrentCHRBank')+1:address(b,'CurrentCHRBank')+12]);modes=bytes(m[address(b,'X5ChrMode')+1:address(b,'X5ChrMode')+12]);queue=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])
   d.call(m,'RdBodyGraphics',p=p,sp=224)
   assert bytes(m[address(b,'CurrentCHRBank')+1:address(b,'CurrentCHRBank')+12])==before and bytes(m[address(b,'X5ChrMode')+1:address(b,'X5ChrMode')+12])==modes
   accepted=offset<78;assert m[0x5c7c]==int(not accepted)
   if accepted:
    packet=list(m[address(b,'VRAM_Buffer1')+offset:address(b,'VRAM_Buffer1')+offset+7]);assert packet[:3]==[63,17,3]and packet[-1]==0
    expect=([12,38,48]if missile else[12,28 if suit else 0,54]);assert packet[3:6]==expect,(suit,missile,packet)
    assert get(m,'VRAM_Buffer1_Offset')==offset+6
   else:assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84])==queue and get(m,'VRAM_Buffer1_Offset')==offset
   rows.append(dict(suit=suit,missile=missile,offset=offset,accepted=accepted,windows1_11_exact=True,palette0_only=True))
  checks['body_CHR_and_palette_roles']=rows
  # Actual original8x8 decoder -> authenticated source pixels -> complete
  # real host PlayerGfx/DrawMetasprite at FIRST pointer consumer. No final
  # hardware rendering/scanline visibility is inferred from this CPU model.
  raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED;rows=[]
  for frame,face,offset in itertools.product(art.BODY,[0,1],[0,4,196]):
   m=pipe.base(b);before_clock=m[0x5c27];consumed=draw(m,frame,face,offset)
   assert consumed and all(x['C']==94 and x['header']%4==0 and x['header']<=56 for x in consumed),(frame,face,consumed)
   pixels,rec=decoded_body(m,frame,face)
   parts,*_=art.native_render(raw,frame,face)
   assert pixels==art.source_pixels(raw,parts),(frame,face,len(pixels),len(art.source_pixels(raw,parts)))
   assert m[0x5c27]==before_clock
   rows.append(dict(frame=frame,facing=face,initial_host_cursor=offset,parts=(len(rec)-1)//4,pixels=len(pixels),first_consumers=consumed))
  checks['all_admitted_body_poses_first_record_and_source_pixels']=rows
  # Both actual outline settings: Rogue's authenticated native art has no
  # added-mask records. Existing source outline selector must leave it exact.
  rows=[]
  for frame,face,outline in itertools.product(art.BODY,[0,1],[0,1]):
   m=pipe.base(b);put(m,PlayerOutlinesOff=outline);draw(m,frame,face,all_objects=True)
   pix,rec=decoded_body(m,frame,face);parts,*_=art.native_render(raw,frame,face)
   assert pix==art.source_pixels(raw,parts)
   rows.append(dict(frame=frame,facing=face,outlines_off=outline,parts=(len(rec)-1)//4,pixels=len(pix)))
  checks['complete_DrawAll_outline_body_cases']=rows
  # Literal source F7/unsupported alternate is empty, never legacy Samus.
  empty=[]
  for frame,alt in[(247,0),(8,1),(255,0)]:
   m=pipe.base(b);m[address(b,'RdSourceAltPalette')]=alt;draw(m,frame,0);assert get(m,'ObjectMetasprite')==0
   empty.append(dict(frame=frame,alternate=alt,ObjectMetasprite=0))
  checks['explicit_source_empty_and_failclosed']=empty
  # Genuine source hurt state -> alternating literal F7/real pose through
  # callback-only source movement and actual PlayerGfx/DrawAll. This does NOT
  # prove native injury admission; old visibility fields remain explicit0.
  rows=[]
  for face in [0,1]:
   m=pipe.base(b,face=face);vis(m);m[0x5c0a]=32;m[0x5c1e]=128
   for age in range(55):
    if age==1:m[0x5c0a]=0
    d.call(m,'RdTxMovement',sp=224)
    frame=m[0x5c03];ptr0=m[address(b,'SmPosePtr')]|m[address(b,'SmPosePtr')+1]<<8
    # Re-render current actual frame without advancing source animation.
    consumed=draw(m,frame,face,all_objects=True)
    assert bool(get(m,'ObjectMetasprite'))==(frame!=247)
    assert (not consumed)==(frame==247)
    rows.append(dict(facing=face,age=age,frame=frame,hurt_clock=m[0x5c1c],blank=(frame==247),pointer_before_render=ptr0,source_action=m[0x5c00]))
  assert any(r['blank']for r in rows)and any(not r['blank']for r in rows)
  checks['direct_source_hurt_F7_draw_chain_preconditioned_visible']=rows
  # Real complete Main: source movement/control frame, final radius box,
  # source center, CHR/body descriptor and actual OAM. Visible preconditions
  # are checked explicitly; lifecycle/injury routing is NOT smuggled in.
  rows=[]
  for kind,face,key,wx,action in itertools.product(['floor','head','side','open'],[0,1],[0,1,128,129],[128,252],[0,3]):
   m=pipe.base(b,kind,face,key,wx);vis(m);m[0x5c00]=action
   if action==3:m[0x5c03]=27;m[0x5c05]=m[0x5c06]=22;m[0x5c01]=8;m[address(b,'Player_Y_Position')]=183
   put(m,SmCeilingHit=1)
   c,row=pipe.idle(m);minimum=min(minimum,row['minimum_SP'])
   assert bbox(m)==expectbox(m),(kind,face,key,wx,action,bbox(m),expectbox(m))
   assert m[0x5c0d]==(get(m,'Player_Y_Position')+16)&255
   if get(m,'ObjectMetasprite'):
    assert m.banks[2]==94 and get(m,'X5ChrMode')==130
    assert get(m,'CurrentCHRBank')==get(m,'SmChrBank')
   row.update(kind=kind,facing=face,keys=key,worldX=wx,initial_action=action,final_frame=m[0x5c03],final_box=bbox(m),visible_preconditions='GuestHurtKind=InjuryTimer=MmDeathFlag=GuestPowerupActive=0')
   rows.append(row)
  checks['actual_full_IdleLoop_Main_final_geometry']=rows
  # Real initialized IRQ/lagNMI at all newly introduced critical boundaries.
  rows=[]
  for name,bank in [('RdBodySelectBox',95),('RdBodyBoxOwn',95),('RdBodyGraphics',95),('RdBodyPublishChr',95),('RdBodyDynamicPrg',95),('HpNativePointerEnd',4),('Z2PostBGBodyBridge',71),('RdBodyBoxSelectBridge',1)]:
   for interrupt in ['IRQ','lagNMI']:
    m=pipe.base(b);vis(m);put(m,SmCeilingHit=1)
    c,row=pipe.idle(m,seam=(address(b,name),bank,interrupt));minimum=min(minimum,row['minimum_SP']);rows.append(dict(entry=name,bank=bank,interrupt=interrupt,**row))
  checks['actual_Main_IRQ_lag_body_seams']=rows
  # Full foreign Main, all old legal identities/variants/modes: application
  # RAM and ordered nonbank writes, returned flags/banks remain exact.
  profiles=[(0,'MarioVariant',0),(0,'MarioVariant',1),(0,'MarioVariant',4),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,None,0),(3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),(6,None,0),(7,None,0),(9,'RlVariant',0),(9,'RlVariant',1),(10,None,0),(11,None,0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(15,'MacVariant',0),(15,'MacVariant',1),(15,'MacVariant',2),(16,None,0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),(19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,None,0)]
  rows=[]
  for(char,key,var),mode in itertools.product(profiles,[0,1]):
   pair=[]
   for bundle in[parent,b]:
    q=seed(bundle,char)
    if key:q.set(key,var)
    q.m[0x5fee]=0
    q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1)
    c,w,_=run(q,'GameLoop',p=0x71);pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
   assert pair[0][:4]==pair[1][:4],('foreign whole Main',char,key,var,mode,pair[0][0],pair[1][0])
   rows.append(dict(raw=char,variant=var,mode=mode,CPU_delta=pair[1][4]-pair[0][4]))
  checks['all_foreign_complete_Main']=rows
  # All actual old selector semantics, including the omitted incomingA save.
  # Actual continuation first STYbbox/LDA1/LDYspeed observes only Y, while
  # X/VDI and caller banks/SP are preserved. A/NZ/C are explicitly dead.
  rows=[]
  for char,var,flags,stale in itertools.product([0,1,2,3,4,8,21],[0,1],FLAGS,[0,17,90,255]):
   pair=[]
   for bundle,name in[(parent,'MegaManCollisionBox'),(b,'RdBodyBoxSelectBridge')]:
    m=d.old.make(bundle);put(m,SelectedCharacter=char,CrossoverBehaviorVersion=1);m[0x5fee]=var
    m[address(bundle,'SafecallA_SMC')+1]=stale
    # Caller lives in A1; direct original leaf resides in LOW126.
    m.page(1,1);m[address(bundle,'CurrentBank')]=129
    c,l,tr=d.service.invoke(m,address(bundle,name),a=91,x=4,y=2,p=flags,sp=224)
    pair.append((c,m,l))
   c,m,l=pair[1];oc,om,ol=pair[0]
   assert c.sp==224 and c.x==oc.x and c.p&76==oc.p&76 and m.banks==om.banks
   assert c.y==(1 if(char,var)==(2,1)else oc.y)
   rows.append(dict(raw=char,variant=var,P=flags,stale_safecallA=stale,CPU_delta=c.processorCycles-oc.processorCycles,minimum_SP=l))
  checks['single_selector_actual_live_ABI_allflag_staleA']=rows
  # Actual full DrawMetasprite / DrawAll for all foreign source families.
  # First helper plate is a real RAM descriptor and must keep its fast path;
  # foreign indirect Mega/Proto/Celeste retain genuine old C leases.
  rows=[]
  for char,key,var in profiles:
   for entry in ['DrawAllMetasprites','DrawMetasprite']:
    pair=[]
    for bundle in[parent,b]:
     q=seed(bundle,char)
     if key:q.set(key,var)
     q.m[0x5fee]=0;q.put(PlayerOutlinesOff=1,PlayerFacingDir=1,Player_Y_Position=144,Player_Y_HighPos=1,Player_X_Position=120,CurrentOAMOffset=4)
     # Genuine graphics owner prepares actual body's linked pointer/page.
     run(q,'PlayerGfxHandler',p=0x71)
     run(q,'HpGraphicsBankCopy',p=0x71)
     if entry=='DrawAllMetasprites':
      reserved,_,_=run(q,'PlayerOAMReservation');q.set('CurrentOAMOffset',reserved.a)
     c,w,_=run(q,entry,x=q.get('ObjectMetasprite'),y=0,p=0x71)
     pair.append((registers(c),app(q),q.m.banks,cleanwrites(q,w),c.processorCycles))
    # Full DrawMetasprite's first consumer overwrites A/NZ/C; returned regs,
    # actual writes and complete application state must consequently match.
    assert pair[0][:4]==pair[1][:4],('foreign full draw',char,key,var,entry,pair[0][0],pair[1][0])
    rows.append(dict(raw=char,variant=var,entry=entry,CPU_delta=pair[1][4]-pair[0][4]))
  checks['all_foreign_complete_DrawMetasprite_DrawAll']=rows
  # Lifecycle API is real code, but not installed shared admission. Preserve
  # approved persistence and private temporal clear policy explicitly.
  rows=[]
  for entry in ['RdBodyNewSession','RdBodyNewLife','RdBodyEnterScene']:
   m=pipe.base(b);m[0x5fb0:0x5fb6]=bytes([255,7,15,3,0x12,0x19]);m[0x5c00:0x5c80]=bytes(range(128));put(m,SavedJoypadBits=128,AreaPointer=0xc2)
   c,l,tr=d.call(m,entry,sp=224)
   assert m[0x5c0b]==255 and m[0x5c3b]==0 and m[0x5c7c]==1
   assert m[address(b,'RdHeld')]==128 and m[address(b,'RdFresh')]==0
   expected=[0,0,0,0,0x99,9]if entry=='RdBodyNewSession'else[255,7,15,3,0x99,0x39]if entry=='RdBodyNewLife'else[255,7,15,3,0x12,0x19]
   assert list(m[0x5fb0:0x5fb6])==expected
   rows.append(dict(entry=entry,persistent_after=expected,future_AreaPointer_ignored=True,CPU=c.processorCycles))
  checks['explicit_uninstalled_lifecycle_APIs']=rows
  proof.update(passed=True,minimum_SP=minimum,limits=['No Mesen/native/PPU/pixel/FPS/audio claim. Original8x8 pixel equality here is a source/OAM/CHR model.','Typed shared lifecycle/injury/visibility is OPEN. Full Main visible tests require GuestHurtKind/InjuryTimer/MmDeathFlag/GuestPowerupActive0; no stale-field normalization was added.','World pickups/items/weapon consumers/authentic audio/menu admission remain open. Public lifecycle APIs have no admitted shared caller yet.','Palette0 body colors only; source Ice palette1 and source alternate69B3 failclosed still need separate world/effect ownership.','Existing standalone deferred-flush SP192 negative is unchanged and separate; actual whole Main seams and frozen ControlStep192 contract retain original scope.'])
 except BaseException as e:
  proof.update(error=str(e),traceback=traceback.format_exc());raise
 finally:
  proof['bindings']=[ref.binding(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'build.json',R/'src/rogue_dawn_host_body.s',P,P.with_suffix('.dbg'),R/'tools/rogue_dawn_host_pipeline_controls_v1.py',R/'tools/rogue_dawn_host_services_controls_v1.py',R/'tools/prepare_rogue_dawn_art_v1.py',ref.ROM]]
  (O/'body-controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,checks={k:len(v)if isinstance(v,list)else v for k,v in checks.items()},minimum_SP=minimum)))

if __name__=='__main__':main()
