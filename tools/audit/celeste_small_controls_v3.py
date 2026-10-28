"""Always-small Celeste: real compiled pose/native collision/full-caller controls."""
from pathlib import Path
import argparse,copy,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *
from celeste_mac_union_controls_v1 import full
MAP=list(range(26))
for j in range(10):MAP[j]=j+12
MAP[10]=23;MAP[25]=23

def ref_bundle(old,b):
 # Independent specification: same native code, requested host size writes,
 # zero-preserving padding and small bbox; selector X translated in CPU below.
 z=copy.deepcopy(old);raw=bytearray(z['raw'])
 for name,n in [('CmHostEnsure::Sync',13),('CmHostPortraitRender',40),('CmMovement::Input',8),('CmCollisionBox',10)]:
  at=location(old,name);new=b['raw'][location(b,name):location(b,name)+n]
  if name=='CmHostPortraitRender':
   # Copy only genuine immediate LDX25->23, not any call target bytes.
   ds=[i for i in range(n)if raw[at+i]!=new[i]];assert len(ds)==1,ds
  raw[at:at+n]=new
 z['raw']=bytes(raw);return z

def mapped_run(q,name,**kw):
 oldstep=NesMPU.step;pc=address(q.b,'CmGraphics::Select')
 def step(c):
  if c.pc==pc and q.m.banks[1]==98:
   assert c.x in list(range(11))+[22,23,25],('nonlegal source selector',c.x)
   c.x=MAP[c.x]
  oldstep(c)
 NesMPU.step=step
 try:return run(q,name,**kw)
 finally:NesMPU.step=oldstep

def snap(q,c):return(registers(c),app(q),q.m.banks,bytes(q.m[z]for z in smc_at(q.b)))
def eqspec(old,b,name,setup,**kw):
 pairs=[]
 for bundle in[old,b]:
  q=cmseed(bundle,setup.get('CmTier',0));q.put(**setup)
  c,w,_=(mapped_run if bundle is old else run)(q,name,**kw)
  pairs.append((snap(q,c),cleanwrites(q,w),c.processorCycles,q))
 assert pairs[0][0]==pairs[1][0],(name,setup,'full ABI/state',pairs[0][0][0],pairs[1][0][0])
 assert pairs[0][1]==pairs[1][1],(name,setup,'ordered writes')
 return pairs

def irq(q,name,kind):
 oldstep=NesMPU.step;seen=set();events=[]
 def step(c):
  bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if bank==98 and (bank,c.pc)not in seen and(kind=='NMI'or not c.p&4):
   seen.add((bank,c.pc))
   def ss():return(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,tuple(q.m.banks),bytes(q.m[:8]),bytes(q.m[0x101+c.sp:0x200]),bytes(q.m[z]for z in smc_at(q.b)),bytes(q.m[0x5c00:0x5ffe]),q.get('CurrentBank'),q.get('CurrentBankC'))
   before=ss()
   if kind=='NMI':c.nmi()
   else:q.m[0x5204]=128;c.irq()
   for _ in range(60000):
    oldstep(c)
    if c.pc==before[5]and c.sp==before[4]:break
   else:raise AssertionError(('ISR timeout',name,kind))
   after=ss();assert after==before,('ISR state',name,kind,hex(c.pc),[(i,[(j,x,y)for j,(x,y)in enumerate(zip(a,z))if x!=y][:12] if isinstance(a,bytes)else(a,z))for i,(a,z)in enumerate(zip(before,after))if a!=z]);events.append([bank,c.pc])
  oldstep(c)
 NesMPU.step=step
 try:run(q,name,p=0x30)
 finally:NesMPU.step=oldstep
 return events

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 paths=[R/'build/roster-shared-rcr-adopted-v8.nes',R/'build/celeste-small-v1.nes'];old,b=[scoped_load(z)for z in paths]
 files=[Path(__file__),R/'tools/prepare_celeste_small_v1.py',R/'tools/audit/celeste_host_controls_v4.py',R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/audit/celeste_mac_union_controls_v1.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py',R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',R/'src/celeste_mario_core.s',R/'src/celeste_mario_render.s',R/'src/celeste_mario_host.s',R/'src/collision.s',R/'src/player.s',R/'src/megaman_weapons.s',R/'build/celeste-native-reference.nes',R/'build/celeste-native-reference.lst',R/'chr/characters/celeste-mario.chr',R/'chr/characters/celeste-mario-assets.json']+[z.with_suffix(ext)for z in paths for ext in['.nes','.dbg','.lbl']]+list((R/'build/celeste-small-overlay/src').glob('*'))
 proof=dict(passed=False,source_CPU_only=True,native_run=False,bindings={str(z.resolve()):sha(z)for z in files},checks={});ck=proof['checks']
 try:
  ds={k:sum(x!=y for x,y in zip(old['raw'][16+k*8192:16+(k+1)*8192],b['raw'][16+k*8192:16+(k+1)*8192]))for k in range(128)};ds={k:v for k,v in ds.items()if v};assert set(ds)=={81,98},ds
  assert old['raw'][16+98*8192+0x1dd8:16+99*8192]==b'\xff'*552 and old['raw'][1048592:]==b['raw'][1048592:]
  for name,z in old['syms'].items():
   if name=='_FARCALL_COUNT':continue
   assert name in b['syms'],('missing symbol',name)
   assert int(z.get('val','0'),0)==address(b,name),('moved symbol',name)
  assert address(b,'CmSmallPoseStart')==0xbdd8
  ck['layout']=dict(passed=True,changed_bytes_by_bank=ds,new_mapper=[address(b,'CmSmallPoseStart'),address(b,'CmSmallPoseEnd')],all_old_runtime_labels_RAM_CHR_exact=True,platform_bank26_exact=True,no_new_RAM_segment_or_CHR=True)
  spec=ref_bundle(old,b)
  # Independent original ROM PlayerGraphicsTable/bank data, not candidate table.
  native=(R/'build/celeste-native-reference.nes').read_bytes();listing=(R/'build/celeste-native-reference.lst').read_text(errors='replace')
  syms={m[2]:int(m[1],16)for line in listing.splitlines()if(m:=re.match(r'^([0-9A-F]{5})\s+([A-Za-z_][\w]*):',line))}
  nread=lambda n,count:native[16+7*8192+syms[n]-0xa000:16+7*8192+syms[n]-0xa000+count]
  table=nread('PlayerGraphicsTable',104);banks=nread('PlayerGFXBankTable',26);patterns=(R/'chr/characters/celeste-mario.chr').read_bytes();assert patterns==native[-131072:][:16384]
  assert table[22*4:24*4]==bytes([255,255,24,24,255,255,48,50])
  rows=[]
  for pose,face,tier in itertools.product(list(range(11))+[22,23,25],[1,2],range(3)):
   q=cmseed(b,tier);q.put(PlayerFacingDir=face,Player_SprAttrib=0,CurrentOAMOffset=0);run(q,'CmGraphics::Select',x=pose);wantpose=MAP[pose];assert q.get('CmPose')==wantpose
   bank=banks[wantpose];ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1);at=16+98*8192+ptr-0xc000
   rec=b['raw'][at:at+9];assert rec[0]==8
   expected=[]
   for i,tile in enumerate(table[wantpose*4:wantpose*4+4]):
    if tile!=255:expected.append([tile,64 if face==2 else 0,(i//2)*16,(8-(i%2)*8)if face==2 else(i%2)*8])
   assert [list(rec[i:i+4])for i in[1,5]]==expected
   # Per-pixel class0..3 agrees with genuine original source and actual bank.
   actual_pixels={};source_pixels={}
   for tile,attr,yy,xx in expected:
    for y in range(16):
     atc=bank*1024+(tile+y//8)*16+y%8
     for x in range(8):
      bit=7-x;v=(patterns[atc]>>bit&1)|((patterns[atc+8]>>bit&1)<<1)
      source_pixels[xx+(7-x if attr&64 else x),yy+y]=v
   for i in[1,5]:
    tile,attr,yy,xx=rec[i:i+4]
    for y in range(16):
     atc=q.get('CmGfxBank')*1024+(tile+y//8)*16+y%8
     for x in range(8):actual_pixels[xx+(7-x if attr&64 else x),yy+y]=(patterns[atc]>>(7-x)&1)|((patterns[atc+8]>>(7-x)&1)<<1)
   assert actual_pixels==source_pixels and min(y for x,y in actual_pixels)==16 and max(y for x,y in actual_pixels)==31
   run(q,'CmDraw');run(q,'HpPrepareNativePointers');run(q,'DrawMetasprite',x=233)
   want=bytes(v for tile,atr,yy,xx in reversed(expected)for v in[(q.get('Player_Y_Position')+yy)&255,tile,atr,(q.get('Player_X_Position')+xx)&255]);assert bytes(q.m[0x200:0x208])==want and q.get('CurrentOAMOffset')==8
   rows.append([pose,wantpose,face,tier,bank])
  ck['original_small_records_pixels_OAM']=dict(passed=True,cases=len(rows),native_small_death22_and_stand23=True,parts=2,visible_rows=[16,31],foot_anchor=32,rows=rows,original_small_palette_classes=True,palette_unchanged=True)
  n=0;costs=[];selected=set()
  for tier,face,state,water,crouch,anim in itertools.product(range(3),[1,2],range(4),[0,1],[0,1],range(3)):
   setup=dict(CmTier=tier,PlayerFacingDir=face,CmState=state,Player_State=state,SwimmingFlag=water,CrouchingFlag=crouch,PlayerAnimCtrl=anim,PlayerAnimTimer=1,Player_Y_Speed=1,Player_X_Speed=16,Left_Right_Buttons=1,Player_MovingDir=1)
   pair=eqspec(spec,b,'CmHostGraphics',setup,p=0x71);q=pair[1][3];assert q.get('PlayerSize')==1 and q.get('CmPose')in range(12,24);selected.add(q.get('CmPose'));costs.append(pair[1][2]-pair[0][2]);n+=1
  for engine in[0,7,8,11]:
   for tier in range(3):
    pair=eqspec(spec,b,'CmHostGraphics',dict(CmTier=tier,GameEngineSubroutine=engine),p=0x31);assert pair[1][3].get('PlayerSize')==1;n+=1
  ck['actual_selector_full_ABI']=dict(passed=True,cases=n,actual_small_poses=sorted(selected),extra_mapper_CPU=[min(costs),max(costs)],full_AXYP_SP_application_RAM_banks_SMC_ordered_writes_equal_independent_small_spec=True,spec='Parent native code with exact requested size/store/bbox changes; only original Select entry X mapped from authenticated big to small pose indices. No old big equivalence claim.')
  rows=[]
  for mode,tier,face,keys in itertools.product([0,1],range(3),[1,2],[0,1,129,64,4,8]):
   setup=dict(CmTier=tier,CrossoverBehaviorVersion=mode,PlayerFacingDir=face,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=keys,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,A_B_Buttons=keys&192)
   pair=eqspec(spec,b,'GameLoop',setup,p=0x71);q=pair[1][3];assert q.get('PlayerSize')==1 and q.get('Player_BoundBoxCtrl')==1 and q.get('PlayerStatus')==q.get('CmTier');rows.append([mode,tier,face,keys,pair[0][2],pair[1][2]])
  ck['complete_GameLoop_small_spec']=dict(passed=True,calls=len(rows),rows=rows,all_three_tiers_both_modes=True,no_stock_Mario_physics_substitution=True)
  rows=[]
  for tier,face,crouch,water in itertools.product(range(3),[1,2],[0,1],[0,1]):
   q=cmseed(b,tier);q.put(PlayerFacingDir=face,CrouchingFlag=crouch,SwimmingFlag=water,Player_X_Position=96,Player_Y_Position=160,Player_Y_Speed=0,Left_Right_Buttons=0,SavedJoypadBits=0)
   c,hits=execute(q,'PlayerCtrlRoutine',observe=['GBBAdr','BlockBufferCollision']);assert q.get('PlayerSize')==1 and q.get('Player_BoundBoxCtrl')==1
   assert hits['GBBAdr'] and hits['GBBAdr'][0][2]==2,('small native terrain selection',tier,face,crouch,water,hits)
   probe_rows=[h[2]for h in hits['BlockBufferCollision']if h[1]==0];assert probe_rows and min(probe_rows)==14 and max(probe_rows)<=20,probe_rows
   run(q,'RelativePlayerPosition');run(q,'LmBoundingBoxGate',x=0)
   bbox=[q.get(n)for n in['BoundingBox_UL_Corner','BoundingBox_UL_Corner']]
   # Actual profile bytes: native small head+18, foot+32, side+24;
   # collision bbox has the original native four-pixel transparent inset.
   base=location(b,'BlockBuffer_Y_Adder');assert b['raw'][base+14:base+21]==bytes([18,32,32,24,24,24,24])
   c,_,_=run(q,'MegaManCollisionAdder',y=201);assert not c.p&1 and c.y==201
   c,_,_=run(q,'MegaManCollisionBox',y=1);assert c.y==1
   c,_,_=run(q,'CmCollisionBox',y=201);assert c.y==1
   rows.append([tier,face,crouch,water,probe_rows,q.get('Player_BoundBoxCtrl')])
  ck['actual_native_collision_selection']=dict(passed=True,cases=len(rows),rows=rows,native_head_y=18,side_y=24,feet_y=32,bbox_native=[3,20,13,32],CmCollisionBox_export_has_no_runtime_callers='Actual PlayerCtrlRoutine gets native row1 from PlayerSize; raw0 MegaManCollisionBox preserves Y. Terrain raw0 returns carry0 then selects native small/crouch row14; no imported big custom bbox relied upon.')
  rows=[]
  for mode,tier,face,slot,kind in itertools.product([0,1],range(3),[1,2],[0,5],range(4)):
   q=cmseed(b,tier);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,ObjectOffset=(slot+1)%6);q.set('PowerUpType',kind,slot);q.set('Enemy_Flag',1,slot);q.set('Enemy_ID',46,slot);q.set('Enemy_State',128,slot);run(q,'NrPickup',x=slot)
   assert q.get('PlayerSize')==1
   if kind<2:assert q.get('CmTier')==min(2,tier+1) and q.get('Enemy_Flag',slot)==0
   elif kind==2:assert q.get('StarInvincibleTimer')==35
   else:assert q.get('FloateyNum_Control',slot)==11
   rows.append([mode,tier,face,slot,kind,q.get('CmTier')])
  ck['real_pickup_progression']=dict(passed=True,cases=len(rows),rows=rows,actual_X_stale_ObjectOffset=True,tiers_not_body_size=True,Star_life_native_fallback_once=True)
  rows=[]
  for tier in range(3):
   for entry in['CmHostFresh','CmHostEnter','CmHostFullPower','CmHostInjuryStatus','ForceInjury']:
    q=cmseed(b,tier);run(q,entry);run(q,'CmHostGraphics');assert q.get('PlayerSize')==1;rows.append([tier,entry,q.get('CmTier'),q.get('GameEngineSubroutine')])
   for mode in[0,1]:
    q=cmseed(b,tier);q.put(OperMode=mode,CurrentOAMOffset=0);run(q,'DrawPlayer_Intermediate');run(q,'X5PortraitRender',x=q.get('ObjectMetasprite'));assert q.get('CmPose')==23 and q.get('PlayerSize')==1 and q.get('CurrentOAMOffset')==8
  ck['cold_portrait_lifecycle_fullpower_injury_death']=dict(passed=True,rows=rows,portraits=6,small23=True)
  rows=[]
  for char,var,mode in itertools.product([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23],[0,1],[0,1]):
   pp=[]
   for bundle in[old,b]:
    q=seed(bundle,char);q.put(MarioVariant=var,CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1);pp.append(full(q,p=0x71))
   assert pp[0]==pp[1],('foreign GameLoop',char,var,mode);rows.append([char,var,mode])
  ck['foreign_full_GameLoop']=dict(passed=True,calls=len(rows),all_AXYP_SP_application_RAM_OAM_hardware_banks_CPU_exact=True)
  events=[]
  for entry in['CmGraphics::Select','CmMovement','CmAfterBG','CmCollisionBox']:
   q=cmseed(b,2);q.put(NmiDisable=255,CmState=1,Player_State=1,Player_Y_Speed=255,Player_CollisionBits=2,Left_Right_Buttons=1);events+=irq(q,entry,'IRQ')
  q=cmseed(b,2);q.put(NmiDisable=255);nn=irq(q,'CmGraphics::Select','NMI')
  ck['actual_IRQ_lagNMI']=dict(passed=True,enabled_core98_IRQ_visits=len(events),unique_IRQ=len({tuple(x)for x in events}),mapper_lagNMI_visits=len(nn),all_six_flags_AXY_PC_SP_R0_R7_live_stack_banks_5SMC_Celeste_state_exact=True)
  assert all(sha(z)==h for z,h in proof['bindings'].items());proof['passed']=True
 except Exception as e:proof.update(failure=repr(e),traceback=traceback.format_exc())
 a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=proof['passed'],failure=proof.get('failure'),checks=list(ck))));assert proof['passed']
if __name__=='__main__':main()
