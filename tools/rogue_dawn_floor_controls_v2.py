"""Qualified internal support worker + source-floor complete callers; no native."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_floor_controls_v1 as base
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
from sunny_integrated_controls_v1 import app,registers
q,get,put,address=v.q,v.get,v.put,v.address
O=R/'build/rogue-dawn-floor-v2';P=base.P
ready,state,down=base.ready,base.state,base.down

def core():
 assert not (O/'controls.json').exists()
 old=v.scoped_load(P/'candidate.nes');b=v.scoped_load(O/'candidate.nes')
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});checks=proof['checks']
 try:
  rows=[]
  for wx,y,j,flags in itertools.product([4,128,252,260,500],[185,192,193],[0,12,255],[0x30,0x31,0x70,0x71]):
   m=ready(b);put(m,RdRoomHi=wx//256,RdX=wx%256,RdY=y,RdRadiusX=4,RdRadiusY=15,
    RdJumpDistance=j,Player_Y_HighPos=1)
   c,z=down(m,a=0x36,x=13,y=87,p=flags)
   committed=y+15<208
   assert get(m,'RdY')==y+committed and get(m,'RdJumpDistance')==(j-committed)&255
   assert bool(c.p&1)==committed
   assert (c.a,c.x,c.y,c.p&~1)==(0x36,13,87,flags&~1)
   rows.append(dict(wx=wx,y=y,jumpDistance=j,flags=flags,committed=committed,CPU=z['CPU'],SP=z['minimum_SP']))
  checks['180_actual_bridge_down_pixel_page_flags_wrap_cases']=dict(cases=len(rows),rows=rows,
   source='Original actual E4A3/E4EC108-case receipt; hostcallback preserves declaredAXYP exceptC, source caller consumes committedC.')
  print('180 bridge/down cases PASS',flush=True)
  # No forcing of action/ground/velocity: actual constructor, real walking,
  # neutral release then physical freshA through completeMain and real NMI.
  rows=[]
  for mode,face in itertools.product([0,1],[0,1]):
   m=ready(b,mode);v.nmi(m);put(m,RdFacing=face)
   pads=[0]*4+[1 if not face else 2]*24+[0]*12+[128]*8+[0]*64
   stages=[];jumps=[];contacts=[]
   for i,pad in enumerate(pads):
    put(m,SavedJoypadBits=pad);c,z=q.mainstep(m);s=state(m)
    if i in[3,27,39,40,41,47,111]:stages.append(dict(update=i,pad=pad,**s))
    if any(pc==address(b,'RdStartJump')and bank==124 for pc,bank,sp in z['trace']):jumps.append(i)
    if any(pc==address(b,'RdGroundCollisionResponse')and bank==124 for pc,bank,sp in z['trace']):contacts.append(i)
    if i==39:assert s['RdAction']==0 and s['RdY']==193 and s['RdGravity']==0,('real stand',mode,face,s)
    if i==40:assert s['RdVY']>=128 and i in jumps,('real jump',mode,face,s)
    v.nmi(m)
   assert get(m,'RdY')==193 and get(m,'RdVY')==0 and any(i>40 for i in contacts)
   rows.append(dict(mode=mode,facing=face,complete_Mains=len(pads),actual_jump_updates=jumps,
    actual_down_contact_updates=contacts,stages=stages,final=state(m)))
  checks['4_complete_Main_walk_release_freshA_descent_landing']=rows
  print('complete Main walk/release/jump PASS',flush=True)
  # The exact prior counterexample still fails on unchanged parent69a.
  m=ready(old);v.nmi(m)
  for i,pad in enumerate([0]*4+[1]*34+[0]*16+([128]*3+[0]*4)*6):
   put(m,SavedJoypadBits=pad);c,z=q.mainstep(m);v.nmi(m)
  assert get(m,'RdAction')==1 and get(m,'RdY')==192 and get(m,'RdVY')==0
  checks['retained_parent_running_stall']=dict(actual_Mains=i+1,final=state(m),trace_report=v.ref.binding(R/'docs/qa/rogue-dawn-run-support-trace-2026-10-29.json'))
  # All foreign real callers are protected by unchanged exact-owner admission.
  rows=[]
  for char,mode in itertools.product(range(24),[0,1]):
   pair=[]
   for bundle in[old,b]:
    m=q.make(bundle,mode);put(m,SelectedCharacter=char,RdVariant=0,SavedJoypadBits=1)
    c,z=q.mainstep(m);nm=q.wake(m)
    class Q:pass
    a=Q();a.b=bundle;a.m=m
    pair.append((registers(c),app(a),q.physical(m),z['CPU'],nm['CPU']))
   assert pair[0][:3]==pair[1][:3],('foreign Main/NMI',char,mode)
   rows.append(dict(character=char,mode=mode,Main_CPU_delta=pair[1][3]-pair[0][3],NMI_CPU_delta=pair[1][4]-pair[0][4]))
  checks['48_actual_foreign_Main_NMI_exact']=rows
  # Full genuine NMI/IRQ at an actual geometry call, standaloneControl192 and
  # naturalMain. No fake IRQ, no second NMI inside NMI or relaxedSMC guard.
  rows=[]
  for entry,sp in [('RdControlStep',192),('IdleLoop',253)]:
   def scene():
    m=ready(b);v.nmi(m);put(m,NmiDisable=255,RdAction=1,RdGravity=26,RdVY=1)
    return m
   m=scene();plain=deep.execute(m,entry,sp);cut=min(plain['trace'],key=lambda a:a[2])
   m=scene();z=deep.execute(m,entry,sp,cut,IRQ=(address(b,'RdaReadRomValue'),97,cut[2]-29))
   assert z['minimum_SP']>=128
   rows.append(dict(entry=entry,entrySP=sp,cut=[hex(cut[0]),cut[1],cut[2]],minimum_SP=z['minimum_SP'],ISR=z['interrupt']))
  checks['actual_deep_Control192_Main_full_lagNMI_IRQ']=rows
  proof.update(passed=True,bindings=[v.ref.binding(p)for p in[Path(__file__),O/'build.json',
   O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',
   R/'docs/qa/rogue-dawn-original-down-pixel-2026-10-29.json',R/'tools/rogue_dawn_scheduler_controls_v3.py',
   R/'tools/rogue_dawn_scheduler_deep_edges_v1.py']],limits=[
   'Typed legal source scenes and genuine compiled Main/NMI/IRQ, not native RAM snapshots or a native route clear.',
   'No original jump constant/action rule changed; unmodified runtime/camera/PPU guards still require ROOT native.',
   'Original terrain decoder and SMB block buffer are distinct declared geometry boundaries.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc())
  p=O/'controls-negative-1.json';i=2
  while p.exists():p=O/f'controls-negative-{i}.json';i+=1
  p.write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,checks=list(checks))))

def support(m,**kw):
 m.page(2,94);put(m,CurrentBankC=222)
 return q.invoke(m,'RdHostFindSupport',**kw)

def main():
 core()
 assert not(O/'support-controls.json').exists()
 old=v.scoped_load(P/'candidate.nes');b=v.scoped_load(O/'candidate.nes');checks={}
 # Public query keeps complete AXYP and all six private source temporaries;
 # internal geometry's only live scratch after the last terrain sample isRh5.
 rows=[]
 for active,slot,flags in itertools.product([0,1],[0,4],[0x30,0x31,0x70,0x71]):
  pair=[]
  for bundle in[old,b]:
   m=base.ready(bundle);put(m,RdY=192,RdX=128,RdRoomHi=0,RdRadiusY=15,RdRadiusX=4)
   for n,val in [('Enemy_Flag',active),('Enemy_ID',0x28),('Enemy_State',0),
    ('Enemy_Y_HighPos',1),('Enemy_Y_Position',208),('Enemy_PageLoc',0),
    ('Enemy_X_Position',112),('Enemy_BoundBoxCtrl',0)]:m[address(bundle,n)+slot]=val
   for i,z in enumerate([0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37]):m[z]=i*17+7
   before=bytes(m[z]for z in[0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37])
   c,z=support(m,a=54,x=13,y=87,p=flags)
   assert bytes(m[a]for a in[0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37])==before
   pair.append(((c.a,c.x,c.y,c.p,c.sp),get(m,'RdFrozenSupport'),get(m,'RdElevator'),q.physical(m),z['CPU']))
  assert pair[0][:-1]==pair[1][:-1]
  rows.append(dict(active=active,slot=slot,flags=flags,exact_publicABI_and_private_scratch=True,CPU_delta=pair[1][-1]-pair[0][-1]))
 checks['16_actual_public_support_ABI']=rows
 # True native moving-platform landing/carry owners remain equivalent; no
 # fake PlatformCollisionFlag is admitted as support.
 rows=[]
 for radius,owner,slot,delta in itertools.product([8,15,4],['PositionPlayerOnHPlat','PositionPlayerOnVPlat','PositionPlayerOnS_Plat'],[0,4],[0,1,255]):
  if owner=='PositionPlayerOnS_Plat'and delta:continue
  pair=[]
  for bundle in[old,b]:
   m=base.ready(bundle);put(m,RdRadiusY=radius,RdRadiusX=4,Player_X_Position=248,Player_PageLoc=0)
   for n,val in [('Enemy_ID',40),('Enemy_Y_Position',176),('Enemy_Y_HighPos',1)]:m[address(bundle,n)+slot]=val
   put(m,R0=delta)
   c,z=q.invoke(m,owner,a=2 if owner=='PositionPlayerOnS_Plat'else 176,x=slot)
   pair.append((base.state(m),(c.a,c.x,c.y,c.p,c.sp),q.physical(m)))
  assert pair[0]==pair[1],('native platform',radius,owner,slot,delta)
  rows.append(dict(radius=radius,owner=owner,slot=slot,delta=delta))
 checks['42_genuine_native_platform_carry_landing']=rows
 # Actual completeMain physical ascent into a native question block, genuine
 # native bump transaction, then descending source pixel/grounding; no actor
 # claim, power, ammo or resource outcome is set by the fixture.
 rows=[]
 for face,wx in itertools.product([0,1],[128,252,260]):
  m=base.ready(b);v.nmi(m);put(m,Player_X_Position=(wx-8)&255,Player_PageLoc=(wx-8)//256,RdFacing=face)
  # Use the real native block buffer; choose the cell under source headcenter.
  at=q.w.life.body.pipe.d.old.tile(m,wx,144,0xc1)
  sawhead=False;sawup=False;air=[]
  for i,pad in enumerate([0]*8+[128]*20+[0]*50):
   put(m,SavedJoypadBits=pad);c,z=q.mainstep(m)
   sawhead|=any(pc==address(b,'NativeRarePlayerHeadCollisionCore')and bank==9 for pc,bank,sp in z['trace'])
   sawup|=get(m,'RdVY')>=128
   if i in[7,8,12,18,28,77]:air.append(dict(update=i,**base.state(m)))
   v.nmi(m)
  assert sawhead and sawup and m[at]!=0xc1,(face,wx,sawhead,m[at],air)
  assert get(m,'RdY')==193 and get(m,'RdVY')==0
  rows.append(dict(facing=face,worldcenterX=wx,actual_native_head_owner=True,block_after=m[at],final=base.state(m),stages=air))
 checks['6_actual_Main_ascent_question_underside_descent_landing']=rows
 out=dict(passed=True,source_CPU_only=True,native_run=False,checks=checks,
  preserved_negative='Unoptimized56e3 support query reached duplicate ten-byte scratch save: Control192/fullNMI/IRQ failed. Current internal worker restores publicABI separately; no bound relaxed.',
  bindings=[v.ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_floor_controls_v1.py',
   O/'controls.json',O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',
   R/'src/rogue_dawn_host_floor_v2.s',R/'build/rogue-dawn-floor-v1/controls-negative-1.json']])
 (O/'support-controls.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(passed=True,additional_checks=list(checks))))
if __name__=='__main__':main()
