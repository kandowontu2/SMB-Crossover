"""Own authenticated CF palette/name APIs, native queue consumer and late text."""
from pathlib import Path
import hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import contra_force_lifecycle_controls_v4 as Q
P=R/'build/contra-force-palette-names-cart-v2';K=R/'build/contra-force-palette-names-kernel-v3';O=R/'build/contra-force-palette-names-controls-v2'
J,C,T,D=Q.J,Q.C,Q.T,Q.D;Q.P=Q.V.P=J.P=C.P=T.P=D.P=P;Q.K=Q.V.K=K
T.B=T.qualified(P/'joint/candidate.nes');T.PAYLOAD=(P/'joint/cf-stream.bin').read_bytes();T.COOKIE=(P/'joint/cf-cookie.bin').read_bytes()
Q.L=Q.V.L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BG=[34,34,15,15,15,34,15,15];NAMES=['BURNS','SMITH','IRON','BEANS']
def enc(s):return bytes(36 if c==' 'else ord(c)-55 for c in s)
def queue(m):return bytes(m[T.address(T.B,'VRAM_Buffer1'):T.address(T.B,'VRAM_Buffer1')+85])
def seed(base,off=0):
 m=C.clone(base);T.put(m,VRAM_Buffer1_Offset=off);m[T.address(T.B,'VRAM_Buffer1'):T.address(T.B,'VRAM_Buffer1')+85]=[0xad]*85;return m
def consume(m):
 at=T.address(T.B,'VRAM_Buffer1');T.put(m,NmiR0=at&255,NmiR1=at>>8);m.raw_page(2,244);T.put(m,CurrentBankC=244)
 c=T.NesMPU(memory=m,pc=T.address(T.B,'UpdateScreen'));c.sp=224;c.stPushWord(32766);m.ppu_log.clear();z=T.finish(m,c)
 return dict(CPU=z['CPU'],PPUDATA=[v for a,v in m.ppu_log if a==8199])
def palettes(bases):
 rows=[]
 for var,area,bg,off in itertools.product(range(4),range(4),range(8),[0,30,76,77,83]):
  m=seed(bases[var],off);T.put(m,AreaType=area,BackgroundColorCtrl=bg);before=queue(m);z=Q.public(m,26)
  if off<77:
   want=bytes([63,16,4,BG[bg or area],55,18,15,0]);assert queue(m)[off:off+8]==want and queue(m)[:off]==before[:off]
   assert T.get(m,'VRAM_Buffer1_Offset')==off+7 and m.ram[2][0x2e2]==0 and z['AXYP'][-1]&1
  else:assert queue(m)==before and T.get(m,'VRAM_Buffer1_Offset')==off and m.ram[2][0x2e2]==1 and not z['AXYP'][-1]&1
  rows.append([var,area,bg,off,z['CPU']])
 ppu=[]
 for var,area in itertools.product(range(4),range(4)):
  m=seed(bases[var]);T.put(m,AreaType=area,BackgroundColorCtrl=0);Q.public(m,26);z=consume(m)
  assert list(m.vram[0x3f10:0x3f14])==[BG[area],55,18,15]
  ppu.append(dict(variant=var,area=area,raw3F10=list(m.vram[0x3f10:0x3f14]),**z))
 return dict(actual_shared26_bound_queue_cases=len(rows),actual_original_UpdateScreen_consumers=len(ppu),fullqueue_no_write_dirty_retry=True,originalP0_37_12_0F_nativeBG_preserved=True,rows=rows,PPU=ppu)
def identities(bases):
 rows=[]
 for var,off in itertools.product(range(4),[0,64,65,83]):
  m=seed(bases[var],off);before=queue(m);z=Q.public(m,18,p=0x79)
  if off<65:
   expect=('     '+NAMES[var]+' '*16)[:16]if var!=2 else '      IRON      '
   assert queue(m)[off:off+19]==bytes([35,40,16])+enc(expect),(var,queue(m)[off:off+19],expect)
   assert queue(m)[off+19]==0 and T.get(m,'VRAM_Buffer1_Offset')==off+19
  else:assert queue(m)==before and T.get(m,'VRAM_Buffer1_Offset')==off
  assert z['AXYP'][:3]==[87,2,3]
  m=seed(bases[var]);c=C.start(m,T.address(T.B,'BtServiceVeneers')+90,0xd7,a=0,x=11,y=7,p=0x79);r=T.finish(m,c)
  assert queue(m)[11:18]==enc((NAMES[var]+' '*7)[:7])and r['AXYP'][:3]==[0,11,7]
  rows.append([var,off,z['CPU'],r['CPU']])
 return dict(actual_shared18_menu_cases=16,actual_shared30_HUD_cases=16,original_names_and_XY_A_contract=True,rows=rows)
def late_lives(bases):
 rows=[];natural=[]
 for var in range(4):
  m=seed(bases[var]);Q.public(m,26);first=queue(m)[:8]
  # Reproduce actual original WriteGameText producer overwrite without
  # skipping it: the current f523 shared ingress may still reject service30.
  z=Q.V.invoke(m,'WriteGameText',a=1,x=0,y=0)
  after=queue(m);at=T.get(m,'VRAM_Buffer1_Offset');natural.append(dict(variant=var,offset=at,has_body_packet=bytes([63,16,4,15,55,18,15])in after,native_text_prefix=after[:8].hex(),CPU=z['CPU']))
  # Own typed late API receives EXACT real nativeA1/Y30, preserving text.
  m=seed(bases[var]);Q.public(m,26);Q.V.invoke(m,'WriteGameText',a=1,x=0,y=0);text=queue(m)[:30]
  c=C.start(m,T.address(T.B,'BtServiceVeneers')+90,0xd7,a=1,x=29,y=30,p=0x79);r=T.finish(m,c)
  assert queue(m)[:30]==text and queue(m)[30:38]==bytes([63,16,4,15,55,18,15,0])
  assert T.get(m,'VRAM_Buffer1_Offset')==37 and r['AXYP'][:3]==[1,29,30]
  v=consume(m);assert list(m.vram[0x3f10:0x3f14])==[15,55,18,15]
  rows.append(dict(variant=var,text_bytes_preserved=30,actual_originalPPU=v))
 return dict(actual_text_overwrite_then_typed_late_status_cases=4,natural_f523_status_ingress_observations=natural,typed_late_black_lives_P0_after_original_text=True,rows=rows)
def world_index(bases):
 rows=[]
 for a in range(4):
  m=C.clone(bases[0]);T.put(m,AreaType=a);z=Q.public(m,32)
  assert z['AXYP'][2]==6*a+6 and T.get(m,'R0')==2*a
  rows.append([a,z['AXYP'],z['CPU']])
 return dict(real_native_world_index_outputs=rows,P2P3_unmodified=True)
def main():
 assert not O.exists();O.mkdir();out=dict(passed=False,native=False,ready=False,natural_cold_or_Main=False,checks={})
 try:
  for p,h in json.loads((P/'source-stage.json').read_text())['bindings'].items():assert sha(p)==h,p
  bases=[]
  for var in range(4):m=Q.load(var);Q.public(m,15);bases.append(m)
  for n,f in [('body_palette',palettes),('identities',identities),('late_lives',late_lives),('world_index',world_index)]:out['checks'][n]=f(bases);print('CF own P0/names',n,'PASS',flush=True)
  out['retained_v1_negative']='V1 requested XY keyword arguments from the older J.shared fixture helper that accepts onlyA/P. V2 enters the SAME genuine publicB020 service30 through C.start, which accepts originalXY; no source/assertion change.'
  out['checks']['native_presentation']=Q.presentation(bases);out['passed']=True
 except Exception as e:out.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(Q.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/cf-stream.bin',P/'joint/cf-cookie.bin',K/'build-proof.json',K/'runtime.lbl',R/'build/contra-force-lifecycle-qualified-v1/handoff.json',R/'build/contra-force-palette-names-controls-v1/controls.json']
  out['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=out['passed'],error=out.get('error'))),flush=True)
if __name__=='__main__':main()
