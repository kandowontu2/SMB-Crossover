"""Finite real IRQ/lag-NMI seams through genuine Thomas Main consumers."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_thomas_natural_foreign_1031_v2 as F
import battletoads_current_loader_controls_v1 as L
import check_thomas_physical_vectors_1031_v2 as P
from check_tmnt_render_oa import address,location
H=F.H;V=F.V;J=F.J;O=R/'build/thomas-natural-vectors-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
NAMES=['ThomasHostCold','ThEnsure','ThMovement','ThomasHostFrame','ThomasC2AcceptedFrame','ThomasHostWeapons','ThGraphics','ThDraw','ThPostTerrain','ThomasHostAfterTerrain','ThMovementIngress','ThPostNativeHot','ThSharedDrawHot']
def run(m,hook=None):
 c=H.start(m,'GameLoop');c,low=H.finish(m,c,hook);assert c.sp==224
 return c,low
def controls(b):
 m=F.C.fresh(b,0);H.put(m,CrossoverMenuIndex=10,FmAlts=64,SelectedCharacter=0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:F.call(m,n)
 H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);F.call(m,'GameMenuRoutine');F.call(m,'PauseRoutine',a=0)
 contexts=[]
 for i in range(1000):
  if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
  H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
  origin=L.fork(m);seen=[]
  def cold(mem,c,n):
   if c.pc==address(b,'ThomasHostCold')and mem.rawtags[1]==3:seen.append(n)
  run(m,cold)
  if seen:contexts.append(('actual_constructor',origin))
  F.consume(m)
 else:raise AssertionError('native parser bound')
 assert contexts,'actual constructor was not naturally consumed'
 for label,keys in[('walk_jump',9),('punch',64)]:
  H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
  contexts.append((label,L.fork(m)));run(m);F.consume(m)
 rows=[]
 points={(address(b,n),3 if n.startswith('Thomas')or n in['ThEnsure','ThMovement','ThGraphics','ThDraw','ThPostTerrain']else((location(b,n)-16)//8192)|128):n for n in NAMES}
 for label,origin in contexts:
  baseline=L.fork(origin);trace=[];near=[]
  def collect(mem,c,n):
   tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   key=(c.pc,tag)
   if key in points:near.append([points[key],0])
   if near and near[-1][1]<16:
    name,i=near[-1];near[-1][1]+=1
    if i in[0,5,12]:trace.append((n,c.pc,tag,c.p,name,H.get(mem,'NmiDisable')))
  c0,lo=run(baseline,collect);trace=list(dict((t[0],t)for t in trace).values())
  for cut,pc,tag,flags,name,lag in trace:
   for kind in['NMI','IRQ']:
    if kind=='IRQ'and flags&4:continue
    z=L.fork(origin);hits=[]
    def inject(mem,c,n):
     if n==cut:hits.append(V.interrupt(mem,c,kind))
    cz,lz=run(z,inject);assert len(hits)==1
    assert(cz.a,cz.x,cz.y,cz.p,cz.sp)==(c0.a,c0.x,c0.y,c0.p,c0.sp),('resumed complete AXYP/SP',label,name,kind,hex(pc))
    assert z.ram[2:]==baseline.ram[2:],('resumed code/state exact',label,name,kind,hex(pc))
    assert bytes(z[3:11])==bytes(baseline[3:11])and bytes(z[512:768])==bytes(baseline[512:768]),('resumed actual scratch/OAM',label,name,kind,hex(pc))
    assert bytes(z[0x15a:0x17b])==bytes(baseline[0x15a:0x17b]),('resumed33SMC',label,name,kind,hex(pc))
    for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed','CrouchingFlag','PlayerFacingDir','ThContextValid']:
     assert H.get(z,n)==H.get(baseline,n),('resumed native/source projection',n,label,kind,hex(pc))
    assert z.rawtags==baseline.rawtags and z.chr_latches==baseline.chr_latches
    rows.append(dict(context=label,worker=name,PC=f'{pc:04X}',bank=tag,lag_guard=lag,**hits[0]))
  print('Thomas actual Main/vector seams PASS',label,len(rows),flush=True)
 return rows
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False)
 try:
  stage=json.loads((J/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  rows=controls(H.C.qualified(J/'candidate.nes'))
  q.update(passed=True,actual_vector_cuts=len(rows),rows=rows,limits=['Actual current IRQ/lag-NMI and resumed Main, no native raster/timing claim','Actual normal-NMI completion separately verified in natural200Main and five foreign cold cohorts','Source audio queue is retained; original KungFu audio driver is not yet acquired'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(F.__file__),Path(L.__file__),Path(P.__file__),Path(V.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','rows','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
