"""Read-only exact00597 composition, actual full callers and interrupt seams."""
from pathlib import Path
import argparse,configparser,itertools,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from celeste_host_controls_v4 import *
from mac_roster_pipe_corner_controls_v1 import trajectory
import mac_roster_terrain_controls_v1 as terrain

def where(b,s):
 if 'seg'not in s:return None
 g=b['segs'][s['seg']]
 if 'ooffs'not in g:return None
 a=int(s.get('val','0'),0)
 return[(int(g['ooffs'],0)-16)//8192,a]if a>=0x8000 else None
def relocations(old,new,bank):
 start=16+bank*8192;aa=old['raw'][start:start+8192];bb=new['raw'][start:start+8192];changed={i for i in range(8192)if aa[i]!=bb[i]};covered=set();rows=[]
 for i in range(8192-18):
  a,z=aa[i:i+18],bb[i:i+18]
  if a==z or not(a[0]==z[0]==141 and a[3]==z[3]==169 and a[5]==z[5]==141 and a[8]==z[8]==169 and a[10]==z[10]==141 and a[13]==z[13]==169 and a[15]==z[15]and a[15]in[32,76]):continue
  if any(a[k]!=z[k]for k in range(18)if k not in[4,9,14]):continue
  if int.from_bytes(a[1:3],'little')!=address(old,'SafecallA_SMC')+1 or int.from_bytes(a[6:8],'little')!=address(old,'FarcallJmpTarget_SMC')+1 or int.from_bytes(a[11:13],'little')!=address(old,'FarcallJmpTarget_SMC')+2 or int.from_bytes(a[16:18],'little')!=address(old,'FarCallCommon'):continue
  before=[a[14]&127,a[4]+256*a[9]];after=[z[14]&127,z[4]+256*z[9]]
  names=[n for n,s in old['syms'].items()if where(old,s)==before and n in new['syms']and where(new,new['syms'][n])==after]
  assert names,('unexplained macro target',bank,i,before,after)
  differences={i+k for k in[4,9,14]if a[k]!=z[k]};covered|=differences
  rows.append(dict(offset=i,old_target=before,new_target=after,genuine_names=names,changed_offsets=sorted(differences)))
 assert changed==covered,('uncovered owner bytes',bank,sorted(changed-covered))
 return dict(changed_bytes=len(changed),rows=rows)
def effects(q,w):return[(i,v)for i,v in w if(0x200<=i<0x300 or 0x2000<=i<0x6000)and not 0x5114<=i<0x5118]
def full(q,name='GameLoop',**kw):
 c,w,_=run(q,name,**kw);return registers(c),app(q),q.m.banks,effects(q,w),c.processorCycles

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 paths=[R/'build/roster-union-celeste-mac-v1.nes',R/'build/celeste-host-visual-v2.nes',R/'build/roster-expansion-mac-pipe-corner-v3.nes'];b,visual,mac=[scoped_load(z)for z in paths]
 assert[sha(z)for z in paths]==['00597cddbff069acbd6fad1571b7b734c5c5f72bc67da49e672565e6c2c4e94d','413239865daea7ec056567f4f53b9ba90ec44866b2fc23a1585a3a548b615615','33d2c7a7bf58aa040f2911d44f1d59dddb4c9b40b3e8727334cf46db74915f97']
 files=[Path(__file__),R/'tools/audit/celeste_host_controls_v4.py',R/'tools/audit/sunny_integrated_controls_v1.py',R/'tools/mac_roster_terrain_controls_v1.py',R/'tools/mac_roster_pipe_corner_controls_v1.py',R/'build/celeste_host_visual_v2_handoff.json',R/'build/mac-roster-pipe-corner-controls-v2.json',R/'build/mac-roster-pipe-terrain-regressions-v2.json',R/'src/celeste_mario_host_entry.s',R/'src/celeste_mario_host_state.inc',R/'src/celeste_mario_host.s',R/'src/little_mac_terrain.s',R/'src/tmnt_mac_probes.inc']+[p.with_suffix(s)for p in paths for s in['.nes','.dbg','.lbl']]
 proof=dict(passed=False,source_CPU_only=True,native_run=False,ROM_sha256=sha(paths[0]),bindings={str(p):sha(p)for p in files},checks={});ck=proof['checks']
 try:
  diff={k:sum(x!=y for x,y in zip(visual['raw'][16+k*8192:16+(k+1)*8192],b['raw'][16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:n for k,n in diff.items()if n}
  assert diff=={0:4,1:2,89:371,93:1616,120:6,125:2,127:2},diff
  assert b['raw'][1048592:]==visual['raw'][1048592:]
  refs={str(k):relocations(visual,b,k)for k in[0,1,120,125,127]}
  start=16+89*8192;changed={i for i in range(8192)if b['raw'][start+i]!=visual['raw'][start+i]};spans=[];covered=set()
  for name,n in[('TnMacHeadProbe',178),('TnMacSideProbe',196)]:
   at=location(b,name)-start;assert at==location(visual,name)-start;covered|=set(range(at,at+n));spans.append(dict(name=name,offset=at,bytes=n))
  assert changed<=covered
  core=next(z for z in b['segs'].values()if z.get('name')=='"LM_CORE"');assert int(core['start'],0)==0xa000 and int(core['size'],0)==3512
  assert b['raw'][16+93*8192+3512:16+94*8192]==visual['raw'][16+93*8192+3512:16+94*8192]
  macrefs={str(k):relocations(mac,b,k)for k in[89,93]}
  for k in[94,95]:assert b['raw'][16+k*8192:16+(k+1)*8192]==mac['raw'][16+k*8192:16+(k+1)*8192]
  assert b['raw'][1048592+668*1024:1048592+708*1024]==mac['raw'][1048592+668*1024:1048592+708*1024]
  for name in['LmMovementGate','LmWeaponsGate','MacRosterTerrainHead','MacRosterTerrainSide','LmStandBlocked','LmSetPose','LmPortraitGate']:
   assert where(mac,mac['syms'][name])==where(b,b['syms'][name]),name
  ck['exact_layout_union']=dict(passed=True,diff_vs_visual=diff,other_banks_CHR_exact=True,rebound_callers=refs,bank89_owned_spans=spans,Mac33d_component_rebindings=macrefs,Mac_core_bytes=3512,Mac_art94_95_and_CHR668_707_exact=True)
  state={n:address(b,n)for n in['CmTier','CmMarker','CmLife','CmArea','CmWorld','CmActive']};assert list(state.values())==list(range(0x5ff8,0x5ffe));assert not b['syms']['CmTier'].get('seg')
  entry=(R/'build/roster-union-celeste-mac-v1-objects/entrypoint.s').read_text();assert '.include "celeste_mario_host_entry.s"'in entry and '.include "celeste_mario.s"'not in entry
  hostentry=(R/'src/celeste_mario_host_entry.s').read_text();assert '.include "celeste_mario_host_state.inc"'in hostentry and '.include "celeste_mario_state.inc"'not in hostentry
  ck['actual_host_state_entry']=dict(passed=True,state=state,exact_raw0_variant4=True,source_entry_host_state_not_old5F98=True)
  rows=[]
  for v,mode,face,pipe,kind in itertools.product(range(3),[0,1],[1,2],[256,736],['solid','pipe']):
   old=trajectory(mac,v,mode,face,pipe,kind);new=trajectory(b,v,mode,face,pipe,kind)
   assert old==new and new['crossed']and not new['false_ceiling']
   rows.append(dict(variant=v,mode=mode,face=face,pipe=pipe,kind=kind,updates=120))
  ck['Mac33d_actual_movement_full_BG']=dict(passed=True,trajectories=len(rows),updates=120*len(rows),every_before_after_xy_vy_collision_bit_exact=True,rows=rows)
  rows=[]
  for v,mode,face,scene in itertools.product(range(3),[0,1],[1,2],['empty','floor','ceiling','pipe']):
   pairs=[]
   for bundle in[mac,b]:
    q=terrain.fresh(bundle,v,0,352,176,0);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=face,Left_Right_Buttons=face)
    if scene=='floor':terrain.floor(q);q.put(Player_Y_Position=177,Player_Y_Speed=3)
    if scene=='ceiling':
     q.put(Player_Y_Position=160-terrain.HEAD[v][0]-2,Player_Y_Speed=252,Player_State=1)
     for xx in[336,352,368]:terrain.cell(q,xx,144,0xc4)
    if scene=='pipe':
     terrain.floor(q);q.put(Player_X_Position=384-terrain.RIGHT[v]+2-256,Player_PageLoc=1,Player_X_Speed=16)
     for yy in[144,160,176,192]:terrain.cell(q,384,yy,0xc4)
    q.m[0x5ff8:0x5ffe]=bytes(range(161,167));pairs.append(full(q,p=0x71))
   assert pairs[0][:4]==pairs[1][:4],('Mac fullcaller',v,mode,face,scene,pairs[0][0],pairs[1][0])
   rows.append(dict(variant=v,mode=mode,face=face,scene=scene,CPU_delta=pairs[1][4]-pairs[0][4]))
  ck['Mac_complete_GameLoop']=dict(passed=True,calls=len(rows),full_AXYP_SP_appRAM_banks_ordered_OAM_nonbank_hardware=True,rows=rows)
  rows=[]
  identities=[(0,'MarioVariant',0),(8,'MarioVariant',1),(1,'ProtoVariant',0),(1,'ProtoVariant',1),(2,'MarioVariant',0),(3,'BillVariant',0),(3,'BillVariant',1),(4,'Z2Variant',0),(4,'Z2Variant',1),(5,'Cv3Variant',0),(5,'Cv3Variant',1),(5,'Cv3Variant',2),(5,'Cv3Variant',3),(6,'MarioVariant',0),(7,'MarioVariant',0),(9,'RlVariant',0),(9,'RlVariant',1),(10,'MarioVariant',0),(11,'MarioVariant',0),(12,'DarkwingVariant',0),(12,'DarkwingVariant',1),(13,'KbVariant',0),(13,'KbVariant',1),(14,'CdVariant',0),(14,'CdVariant',1),(16,'MarioVariant',0),(17,'M3Variant',0),(17,'M3Variant',1),(18,'VvVariant',0),(18,'VvVariant',1),(18,'VvVariant',2),(18,'VvVariant',3),(19,'TnVariant',0),(19,'TnVariant',1),(19,'TnVariant',2),(19,'TnVariant',3),(20,'IcVariant',0),(20,'IcVariant',1),(21,'RcVariant',0),(21,'RcVariant',1),(23,'MarioVariant',0)]
  for char,key,var in identities:
   for mode in[0,1]:
    pairs=[]
    for bundle in[visual,b]:
     q=seed(bundle,char);q.set(key,var);q.put(CrossoverBehaviorVersion=mode,GameTimerDisplay=4,PlayerEntranceCtrl=2,SavedJoypadBits=1,Left_Right_Buttons=1);q.m[0x5ff8:0x5ffe]=bytes(range(161,167));pairs.append(full(q,p=0x71));assert bytes(q.m[0x5ff8:0x5ffe])==bytes(range(161,167))
    assert pairs[0][:4]==pairs[1][:4],('foreign fullcaller',char,key,var,mode)
    rows.append(dict(char=char,key=key,variant=var,mode=mode,CPU_delta=pairs[1][4]-pairs[0][4]))
  ck['foreign_complete_GameLoop']=dict(passed=True,calls=len(rows),full_AXYP_SP_appRAM_banks_ordered_OAM_nonbank_hardware=True,rows=rows)
  rows=[]
  for tier,mode,face,buttons in itertools.product(range(3),[0,1],[1,2],[0,1,129,64]):
   pairs=[]
   for bundle in[visual,b]:
    q=cmseed(bundle,tier);q.put(CrossoverBehaviorVersion=mode,PlayerFacingDir=face,Player_MovingDir=face,SavedJoypadBits=buttons,A_B_Buttons=buttons&192,Left_Right_Buttons=buttons&3,GameTimerDisplay=4,PlayerEntranceCtrl=2)
    pairs.append(full(q,p=0x71))
   assert pairs[0][:4]==pairs[1][:4],('Celeste fullcaller',tier,mode,face,buttons)
   rows.append(dict(tier=tier,mode=mode,face=face,buttons=buttons,CPU_delta=pairs[1][4]-pairs[0][4]))
  ck['Celeste_complete_GameLoop']=dict(passed=True,calls=len(rows),full_AXYP_SP_appRAM_banks_ordered_OAM_nonbank_hardware=True,rows=rows)
  # Real Mac bank89->93->native BG seams with actual IRQ and regular/lag NMI.
  seams=[]
  for scene in['head','side']:
   def arena(lag=False):
    q=terrain.fresh(b,2,0,352,164,252)if scene=='head'else terrain.fresh(b,1,0,371,176)
    if scene=='head':
     for xx in[336,352,368]:terrain.cell(q,xx,144,0xc4)
    else:
     terrain.floor(q)
     for yy in[144,160,176,192]:terrain.cell(q,384,yy,0xc4)
    q.put(NmiDisable=255 if lag else 0);return q
   _,_,pcs=terrain.run(arena(),'PlayerBGCollision')
   names=['TnMacHeadProbe','MacRosterTerrainHead','BlockBufferColli_Head']if scene=='head'else['TnMacSideProbe','MacRosterTerrainSide','LmVisibleSideProbe']
   boundaries=[next((pc,k)for pc,k in pcs if pc==address(b,n))for n in names]
   for kind,lag,(target,targetbank)in itertools.product(['IRQ','NMI'],[False,True],boundaries):
    q=arena(lag);oldstep=NesMPU.step;fired=[False];smc=smc_at(b)
    def irq_step(c):
     bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
     if not fired[0]and c.pc==target and bank==targetbank:
      fired[0]=True;before=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]))
      if kind=='NMI':c.nmi()
      else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(b,'IrqScrollSplit')
      for _ in range(50000):
       oldstep(c)
       if c.pc==before[5]and c.sp==before[4]:break
      else:raise AssertionError(('interrupt timeout',kind,scene))
      after=(c.a,c.x,c.y,c.p&207,c.sp,c.pc,tuple(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'),bytes(q.m[z]for z in smc),bytes(q.m[0x101+c.sp:0x200]));assert before==after
     oldstep(c)
    NesMPU.step=irq_step
    try:terrain.run(q,'PlayerBGCollision')
    finally:NesMPU.step=oldstep
    assert fired[0];seams.append(dict(scene=scene,kind=kind,lag=lag,bank=targetbank,PC=target,AXYP_PC_SP_banks_five_SMC_live_stack_exact=True))
  n=0
  for fn in['CmHostMovement','CmHostGraphics','CmHostColors','CmHostPortraitRender']:
   q=cmseed(b,2);q.put(CurrentOAMOffset=0,VRAM_Buffer1_Offset=0);run(q,'DrawPlayer_Intermediate');_,_,cnt=run(q,fn,a=87,x=29,y=0,p=0x30,irq=True);n+=cnt
  ck['actual_interrupts']=dict(passed=True,Mac_IRQ_NMI_seams=seams,Celeste_enabled_IRQ_boundaries=n,actual_five_SMC_mapper_live_stack=True)
  for p,h in proof['bindings'].items():assert sha(p)==h
  proof['passed']=True
 except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=True,sha256=sha(a.output),checks=list(ck))))
if __name__=='__main__':main()
