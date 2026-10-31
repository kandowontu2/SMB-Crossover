"""First actual experimental native-first group/render diagnosis, no admission."""
from pathlib import Path
import hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_palette_names_controls_v2 as V
Q,J,C,T,D=V.Q,V.J,V.C,V.T,V.D;P=R/'build/contra-force-p1-cart-v2';K=R/'build/contra-force-p1-kernel-v1';O=R/'build/contra-force-p1-native-first-controls-v2'
V.P=Q.P=Q.V.P=J.P=C.P=T.P=D.P=P;Q.K=Q.V.K=K
T.B=T.qualified(P/'joint/candidate.nes');T.PAYLOAD=(P/'joint/cf-stream.bin').read_bytes();T.COOKIE=(P/'joint/cf-cookie.bin').read_bytes()
Q.L=Q.V.L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def original(m):return Q.V.original(m)
def scene(var=0,shot=True,world=True):
 m=Q.load(var);Q.public(m,15);T.put(m,SavedJoypadBits=0);Q.public(m,0)
 T.put(m,FrameCounter=0,SpriteShuffleOffset=0,RgOamUsed=0,RgOamFirst=0,RgOamRotation=0,GuestOamRotationActive=0,CurrentOAMOffset=0,SmFreezeRenderState=1,SmFreezePaletteControl=2)
 for i in range(24):m[T.address(T.B,'ObjectMetasprite')+i]=0;m[T.address(T.B,'SprObject_SprAttrib')+i]=(i&3)
 for n in ['Block_State','FloateyNum_Control','Misc_State']:
  for i in range(9):m[T.address(T.B,n)+i]=0
 T.put(m,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1)
 if world:
  m[T.address(T.B,'ObjectMetasprite')+1]=T.address(T.B,'METASPRITE_KOOPA_WALKING_1')
  for n,v in dict(Enemy_Flag=1,Enemy_ID=0,Enemy_X_Position=184,Enemy_PageLoc=0,Enemy_Y_Position=176,Enemy_Y_HighPos=1,Enemy_MovingDir=1,Enemy_SprAttrib=1).items():m[T.address(T.B,n)]=v
 if shot:
  i=10
  for at,v in [(0x382+i,1),(0x334+i,28),(0x31a+i,5),(0x34e+i,144),(0x368+i,176),(0x300+i,0)]:m.ram[2][at]=v
 Q.V.invoke(m,'PlayerGfxHandler')
 return m

def draw(m,target='FwNativeDrawAll'):
 hits=[];lo=T.address(T.B,'DrawAllMetasprites');entry=Q.L['CfP1LateEntry'];early=Q.L['CfHostDraw']
 def hook(c,i):
  raw=m.rawtags[(c.pc-32768)//8192]if c.pc>=32768 else-1
  if c.pc==lo and raw==0x84:hits.append('nativeDraw')
  if c.pc==early and raw==3:hits.append('earlyCF')
  if c.pc==entry and raw==3:hits.append('lateCF')
 z=Q.V.invoke(m,target,a=0x57,p=0x79,hook=hook)
 return dict(hits=hits,result=z,rawmaps=m.rawtags,source_phase=m.ram[2][0x2df],Last=T.get(m,'SmFreezeLastBlue'),Pending=T.get(m,'SmFreezePalettePending'),Turn=T.get(m,'SmFreezeTurn'),packet=list(m[T.address(T.B,'SmFreezePalettePacket'):T.address(T.B,'SmFreezePalettePacket')+7]),CHR=m.chr_latches)
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,ready=False,checks={})
 try:
  for p,h in json.loads((P/'source-stage.json').read_text())['bindings'].items():assert sha(p)==h,p
  m=scene();saved=bytes(m[T.address(T.B,'SprObject_SprAttrib'):T.address(T.B,'SprObject_SprAttrib')+24]);before=original(m);rows=[]
  for age in range(4):
   z=draw(m);rows.append(z);assert z['hits']==['nativeDraw','earlyCF','lateCF'],z
   assert original(m)==before and bytes(m[T.address(T.B,'SprObject_SprAttrib'):T.address(T.B,'SprObject_SprAttrib')+24])==saved
   assert all(m[514+i]&24==0 for i in range(0,256,4)),('unstripped tag',age)
   assert z['source_phase']==0 and z['Last']in[192,193]and z['Pending']in[128,192],z
  assert [z['Last']for z in rows]==[193,192,193,192],rows
  out['checks']['4draw_complete_groups_initial']=rows
  # Genuine injury/status row6 WITHOUT early-token remains original no-opC0.
  no=Q.public(m,6,p=0x79);assert no['AXYP']==[87,2,3,0x78],no
  out['checks']['ordinary_service6_no_producer']=no
  # Retain the first stale-cookie counterexample truthfully.
  m.ram[2][0x1fe0]^=1;bad=draw(m);out['checks']['stale_cookie_after_valid_epoch']=bad
  assert bad['hits']==['nativeDraw'] and bad['Last']not in[192,193]and bad['Pending']==0,('stale CF producer after ROMauth rejection',bad)
  out['retained_v1_fixture_negative']='V1 called forcedP3 Goomba a nativeP1 conflict because actorattr1 was seeded, but source descriptor overrides it. Compiledmask103=0 correctly kept worldvisible and choseallCFepochs. V2 uses genuine Koopa106/mask2, preserving forcedpalette semantics and all expectations.'
  out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(V.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/cf-stream.bin',P/'joint/cf-cookie.bin',K/'build-proof.json',K/'runtime.lbl',R/'build/contra-force-p1-native-first-controls-v1/controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'))),flush=True)
if __name__=='__main__':main()

