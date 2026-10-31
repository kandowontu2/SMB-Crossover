from pathlib import Path
import sys,json,traceback,hashlib
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_split_loader_controls_v1 as T
H=T.H;address=T.address
from check_tmnt_render_oa import load
O=R/'build/bowser-gameplay-component-controls-v2';J=R/'build/bowser-gameplay-component-v3/joint'
def rc(m,n,**kw):
 c=H.start(m,n,**kw);c.a=3
 c,lo=H.finish(m,c);assert c.sp==kw.get('sp',224);return c,lo

def main():
 O.mkdir(exist_ok=False);q={'passed':False,'source_CPU':True,'native':False}
 try:
  b=load(J/'candidate.nes');rows=[]
  for variant in [0,8]:
   m=T.make(b,FmAlts=variant,CurrentPlayer=0,Player_State=0,Player_Y_Position=176,Player_X_Position=120)
   T.call(m,'BwLoad');rc(m,'BwConstruct');
   for page in [0,1]:
    for col in range(16): m[address(b,'Block_Buffer_1')+page*208+176+col]=128
   assert m.ram[3][0x1e29]==(5 if variant else 34)
   trace=[]
   for i in range(90):
    keys=1|(128 if 8<=i<16 else 0)|(64 if i==0 else 0)
    H.put(m,SavedJoypadBits=keys,FrameCounter=i)
    rc(m,'BwMovement')
    # Execute genuine native terrain routine and source continuation separately;
    # no abstract floor callback is linked into this actual host component.
    T.call(m,'PlayerBGCollision')
    rc(m,'BwWeaponTail')
    trace.append([i,H.get(m,'Player_X_Position'),H.get(m,'Player_PageLoc'),H.get(m,'Player_Y_Position'),H.get(m,'Player_Y_Speed'),H.get(m,'Player_State'),m.ram[3][0x1e16],m.ram[3][0x1e80],m.ram[3][0x1e8a]])
   assert trace[-1][1]+256*trace[-1][2]>120
   assert min(r[3]for r in trace[:30])<176,trace[:30]
   H.put(m,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0)
   rc(m,'BwConstruct');hp=m.ram[3][0x1e29];H.put(m,InjuryTimer=0);rc(m,'BwInjury');assert m.ram[3][0x1e29]==hp-1
   rc(m,'BwInjury');assert m.ram[3][0x1e29]==hp-1
   H.put(m,CurrentPlayer=1);rc(m,'BwEnsure');assert m.ram[3][0x1e29]==hp
   H.put(m,CurrentPlayer=0);rc(m,'BwEnsure');assert m.ram[3][0x1e29]==hp-1
   # Full original record geometry is copied by real source graphics adapter.
   gfx=[]
   for pose in range(4 if variant else 9):
    for face in [1,2]:
     m.ram[3][0x1e16]=pose;H.put(m,PlayerFacingDir=face)
     c,lo=rc(m,'BwGraphics');count=m.ram[3][0x1e40]
     assert count in([28]if variant else[40,44,48])
     assert H.get(m,'SmPosePtr')==(0x40) and m[address(b,'SmPosePtr')+1]==0xde
     assert m.rawtags[2]==3 and H.get(m,'ObjectMetasprite')==0xe9
     gfx.append([pose,face,count,c.processorCycles,lo])
   rows.append({'variant':variant,'trace':trace,'graphics':gfx,'HP_and_2player':True})
  q.update(passed=True,rows=rows,limits='Explicit source movement/native terrain/weapon-tail adapter sequence; shared ingress/cold Main not yet installed')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}));assert q['passed']
if __name__=='__main__':main()
