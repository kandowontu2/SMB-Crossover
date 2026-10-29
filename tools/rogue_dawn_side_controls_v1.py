"""Half-open source side boundary and real post-question movement callers."""
from pathlib import Path
import csv,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_floor_controls_v1 as base
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
from sunny_integrated_controls_v1 import app,registers
q,get,put,address=v.q,v.get,v.put,v.address
P=R/'build/rogue-dawn-floor-v4';O=R/'build/rogue-dawn-side-v1'

def ready(b,mode=0,px=337):
 m=base.ready(b,mode);put(m,AreaPointer=0x25);q.invoke(m,'GetAreaDataAddrs')
 put(m,EnemyDataOffset=0,EnemyObjectPageLoc=0,EnemyObjectPageSel=0)
 assert get(m,'EnemyDataLow')+256*get(m,'EnemyDataHigh')==address(b,'E_GroundArea6')
 camera=max(0,px-91)
 v.nmi(m);put(m,Player_X_Position=px&255,Player_PageLoc=px//256,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera//256)
 q.invoke(m,'GetScreenPosition')
 return m

def wx(m):return get(m,'Player_X_Position')+256*get(m,'Player_PageLoc')

def main():
 assert not(O/'controls.json').exists()
 old=v.scoped_load(P/'candidate.nes');b=v.scoped_load(O/'candidate.nes')
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});checks=proof['checks']
 try:
  rows=[]
  for x,radius,delta,left,flags in itertools.product([4,128,252,260,500],[4,8,15],[-1,0,1],[False,True],[0x30,0x31,0x70,0x71]):
   m=base.ready(b);put(m,RdX=x&255,RdRoomHi=x//256,RdY=208-radius+delta,
    RdRadiusX=4,RdRadiusY=radius,Player_Y_HighPos=1)
   m.page(2,94);put(m,CurrentBankC=222)
   scratch=[0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37]
   for i,a in enumerate(scratch):m[a]=i*17+7
   before=bytes(m[a]for a in scratch);image=q.image(m);banks=q.physical(m)
   c,z=q.invoke(m,'RdHostMoveLeft'if left else'RdHostMoveRight',a=54,x=13,y=87,p=flags)
   # The preserved world-left boundary rejects pageFFFF; that is separate
   # from the floor extent and remains an intentional negative control.
   committed=delta<=0 and not(left and x<=4);after=get(m,'RdX')+256*get(m,'RdRoomHi')
   assert after==(x+(-1 if left else 1)*committed)&65535,(x,radius,delta,left,flags,after,c.p)
   assert get(m,'RdY')==208-radius+delta and bool(c.p&1)==committed
   assert(c.a,c.x,c.y,c.p&~1)==(54,13,87,flags&~1)
   assert bytes(m[a]for a in scratch)==before and q.image(m)==image and q.physical(m)==banks
   rows.append(dict(centerX=x,radius=radius,overlap_delta=delta,left=left,flags=flags,
    committed=committed,actual_X=after,CPU=z['CPU'],minimum_SP=z['minimum_SP']))
  checks['360_actual_C94_side_callbacks_floor_alignment_overlap_pages_flags_ABI']=dict(cases=len(rows),rows=rows)
  print('360 actual side callback cases PASS',flush=True)
  # Fixed real scene: actual first question constructor, actual source jump,
  # landing and physical Left/Right. No health/gear/form/actor outcomes set.
  rows=[]
  for mode,left in itertools.product([0,1],[False,True]):
   pair=[]
   for bundle in[old,b]:
    m=ready(bundle,mode)
    tiles={x:q.w.life.body.pipe.d.old.tile(m,x,144,t)for x,t in[(320,0x51),(336,0xc1),(352,0x51),(368,0xc0),(384,0x51)]}
    pads=[0]*8+[128]*25+[0]*65+[2 if left else 1]*40+[0]*12+[128]*8+[0]*62
    stages=[];born=[];jumps=[];xs=[]
    for i,pad in enumerate(pads):
     put(m,SavedJoypadBits=pad);c,z=q.mainstep(m)
     if any(pc==address(bundle,'RdStartJump')and bank==124 for pc,bank,sp in z['trace']):jumps.append(i)
     for slot in range(6):
      if m[address(bundle,'Enemy_Flag')+slot]and m[address(bundle,'Enemy_ID')+slot]==0x2e and not born:
       born.append(dict(update=i,slot=slot,pickup=m[address(bundle,'InvPickup')+slot],owner=m[address(bundle,'InvPickupOwner')+slot]))
     if i in[7,13,32,97,105,117,137,149,150,151,157,219]:stages.append(dict(update=i,pad=pad,playerX=wx(m),**base.state(m)))
     if 97<=i<=137:xs.append(wx(m))
     v.nmi(m)
    assert born and born[0]['pickup']==0xd8 and born[0]['owner']==2 and m[tiles[336]]!=0xc1
    pair.append(dict(candidate='df44_parent'if bundle is old else'private_successor',actual_Mains=len(pads),
     birth=born,stages=stages,jump_updates=jumps,horizontal_X_values=xs,final=base.state(m)))
   assert len(set(pair[0]['horizontal_X_values']))==1 and pair[0]['horizontal_X_values'][0]==337
   end=pair[1]['horizontal_X_values'][-1]
   assert (337-end if left else end-337)>=48,(mode,left,end)
   assert pair[1]['stages'][9]['RdVY']>=128 and 150 in pair[1]['jump_updates']
   assert pair[1]['final']['RdY']==193 and pair[1]['final']['RdVY']==0
   rows.append(dict(mode=mode,left=left,comparison=pair))
  checks['4_actual_Main_birth_floor_walk_release_freshA_landing_comparisons']=rows
  print('4 complete Main post-question movement comparisons PASS',flush=True)
  # Genuine walls/head/feet must remain effective; altered side range cannot
  # let a body overlap a pipe or turn a floor into a phantom side wall.
  rows=[]
  for mode,left,page in itertools.product([0,1],[False,True],[0,1]):
   bundle=b;m=ready(bundle,mode,px=240+256*page if not left else 272+256*page)
   # Native pipe column256..271 from144 through207, directly above floor208.
   for x in range(512,768,16):q.w.life.body.pipe.d.old.tile(m,x,208,0x54)
   for y in range(144,208,16):q.w.life.body.pipe.d.old.tile(m,256+256*page,y,0x54)
   for i in range(4):put(m,SavedJoypadBits=0);q.mainstep(m);v.nmi(m)
   start=wx(m);moved=[]
   for i in range(36):
    put(m,SavedJoypadBits=2 if left else 1);q.mainstep(m);moved.append(wx(m));v.nmi(m)
   final=wx(m);center=get(m,'RdX')+256*get(m,'RdRoomHi')
   assert final!=start,(mode,left,page,start,final,center)
   if left:assert center-4>=272+256*page,(mode,left,page,start,final,center,moved)
   else:assert center+4<256+256*page,(mode,left,page,start,final,center,moved)
   assert len(set(moved[-8:]))==1 and get(m,'RdY')==193
   rows.append(dict(mode=mode,left=left,page=page,start=start,final=final,source_center=center,actual_Mains=36))
  checks['8_actual_Main_pipe_side_stop_page_edges']=rows
  # Every changed byte outsideA95 must be an actual +3 relocated cold target.
  a,z=old['raw'],b['raw'];covered=set();reloc=[];smc=address(b,'FarcallJmpTarget_SMC')
  for at in range(16,len(a)-10):
   bank=(at-16)//8192
   if bank==95:continue
   if a[at]==z[at]==0xa9 and a[at+2:at+6]==z[at+2:at+6]==bytes([0x8d,(smc+1)&255,(smc+1)>>8,0xa9]) and a[at+7:at+10]==z[at+7:at+10]==bytes([0x8d,(smc+2)&255,(smc+2)>>8]):
    before=a[at+1]+256*a[at+6];after=z[at+1]+256*z[at+6]
    if before!=after:
     assert after==before+3 and 0xa600<=before<0xbf00
     covered.update([at+1,at+6]);reloc.append(dict(bank=bank,before=hex(before),after=hex(after)))
   if bank==94 and a[at]==z[at]==0x20:
    before=int.from_bytes(a[at+1:at+3],'little');after=int.from_bytes(z[at+1:at+3],'little')
    if before!=after and before==address(old,'RdHostDispatch'):
     assert after==address(b,'RdHostDispatch')==before+3
     covered.update([at+1,at+2]);reloc.append(dict(bank=bank,before=hex(before),after=hex(after)))
  outside=[i for i,(x,y)in enumerate(zip(a,z))if x!=y and(i-16)//8192!=95]
  assert set(outside)<=covered,[hex(i)for i in outside if i not in covered]
  checks['external_genuine_relocated_operands']=dict(changed_bytes=len(outside),relocations=reloc)
  rows=[]
  for char,mode in itertools.product(range(24),[0,1]):
   pair=[]
   for bundle in[old,b]:
    m=q.make(bundle,mode);put(m,SelectedCharacter=char,RdVariant=0,SavedJoypadBits=1)
    c,z=q.mainstep(m);nm=q.wake(m)
    class Q:pass
    obj=Q();obj.b=bundle;obj.m=m
    pair.append((registers(c),app(obj),q.physical(m),z['CPU'],nm['CPU']))
   assert pair[0][:3]==pair[1][:3],('foreign',char,mode)
   rows.append(dict(character=char,mode=mode,Main_CPU_delta=pair[1][3]-pair[0][3],NMI_CPU_delta=pair[1][4]-pair[0][4]))
  checks['48_foreign_actual_Main_NMI']=rows
  rows=[]
  for action,pad in itertools.product([0,1,2,3,4,6],[0,128]):
   def scene():
    m=base.ready(b);v.nmi(m);put(m,RdAction=action,RdHeld=pad,RdFresh=pad,RdClock=0,NmiDisable=255)
    if action==3:put(m,RdRadiusY=8,RdAnimFrame=27,RdAnimReset=22,RdAnimIndex=22)
    return m
   m=scene();plain=deep.execute(m,'RdControlStep',192);cut=min(plain['trace'],key=lambda a:a[2])
   m=scene();z=deep.execute(m,'RdControlStep',192,cut,IRQ=(address(b,'RdaReadRomValue'),97,cut[2]-29))
   assert z['minimum_SP']>=128,(action,pad,z['minimum_SP'])
   rows.append(dict(action=action,pad=pad,entrySP=192,cut=[hex(cut[0]),cut[1],cut[2]],minimum_SP=z['minimum_SP']))
  checks['12_Control192_full_real_lagNMI_IRQ']=rows
  # Compact actual native first negative facts; originals remain untouched.
  native=R/'build/verification/rogue-dawn-question-target-native-easy-v1'
  result=json.loads((native/'result.json').read_text());trace=list(csv.DictReader((native/'trace.csv').open()))
  end=trace[-1];active=[r for r in trace if int(r['loops'])>int(end['loops'])-300]
  assert result['passed']is False and result['reason']=='Controller stationary for 300 genuinely active completed updates'
  assert {r['x']for r in active}=={'337'} and {r['y']for r in active}=={'177'} and {r['mask']for r in active}=={'0','2'}
  checks['actual_native_negative']=dict(result=result,final300_Mains=dict(x=337,y=177,poll_rows=len(active),neutral_poll_rows=sum(r['mask']=='0'for r in active),left_poll_rows=sum(r['mask']=='2'for r in active),VX=sorted({int(r['vx'])for r in active})),
   scope='Native source action/probe RAM was not logged. The independent completeMain source scene reproduces the exact position/velocity symptom and real question birth; this is not a claimed native RAM replay.')
  proof.update(passed=True,minimum_SP=min(r['minimum_SP']for r in checks['12_Control192_full_real_lagNMI_IRQ']),
   bindings=[v.ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',
    R/'docs/qa/rogue-dawn-original-side-extent-2026-10-29.json',native/'result.json',native/'trace.csv',native/'inputs.csv']],
   limits=['CPU source/host external geometry proof, not native successor acceptance or route clear.',
    'Prior floor walk/release/jump controls asserted action/vertical stages but omitted horizontal displacement; preserved as a coverage gap, not retroactively a walking pass.',
    'Horizontal leading-edge convention, original jump/physics/kernel, head first-solid behavior, guards, controller, resource acquisition and audio are unchanged.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc())
  i=1
  while(O/f'controls-negative-{i}.json').exists():i+=1
  (O/f'controls-negative-{i}.json').write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,minimum_SP=proof['minimum_SP'],checks=list(checks))))
if __name__=='__main__':main()
