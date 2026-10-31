"""Targeted actual pending-ROM/lives and WriteGameText retry on combined dfdb."""
from pathlib import Path
import hashlib,json,itertools,traceback
R=Path(__file__).resolve().parents[2]
P=Path(__file__).with_name('smb2_late_lives_controls_v1.py')
J=R/'build/coherent62-lives-fixes-v1/joint'
O=R/'build/smb2-late-lives-combined-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
H=R/'build/smb2-late-lives-palette-v6/handoff-qualified-v2.json'
assert sha(H)=='cdaecb1a19548d1fa5de26885a9d5b636228d3d2ecfc1bb599a63f1c9b3d8c69'
h=json.loads(H.read_text())
def verify():
 for p,v in h['bindings'].items():assert sha(p)==v,p
 assert sha(J/'candidate.nes')=='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7'
verify()
s=P.read_text().split('def main():',1)[0].replace("J=R/'build/smb2-late-lives-palette-v4/joint'", "J=R/'build/coherent62-lives-fixes-v1/joint'")
ns={'__file__':str(P),'__name__':'_targeted_late_lives_source'}
exec(compile(s,str(P),'exec'),ns)
A,C,M=map(ns.get,['A','C','M'])
assert not O.exists();O.mkdir()
q=dict(passed=False,native=False,candidate=sha(J/'candidate.nes'),checks={})
try:
 rows=[]
 for var,mode in itertools.product(range(4),range(2)):
  m,z=ns['cold'](J,var,mode)
  rows.append(dict(variant=var,mode=mode,**z))
 q['checks']['actual_pending_ROM3_cold_lives_entrance_64Main_TOTAL']=rows
 print('8 actual pending-order cold/lives cohorts +64Main TOTAL PASS',flush=True)
 rows=[]
 for var,mode in itertools.product(range(4),range(2)):
  m=ns['seed'](J,var,mode)
  M.put(m,OperMode=1,ScreenRoutineTask=6,BackgroundColorCtrl=0,VRAM_Buffer1_Offset=83,VRAM_Buffer_AddrCtrl=3,S2PaletteAck=0)
  C.invoke(m,'WriteGameText',A=1)
  assert m.get('S2PaletteAck')==255 and m.get('VRAM_Buffer1_Offset')==30
  at=m.lab['VRAM_Buffer1'];before=list(m.ram[at:at+31])
  A.interrupt(m,0);assert m.get('VRAM_Buffer_AddrCtrl')==0
  C.invoke(m,'WriteGameText',A=1);after=list(m.ram[at:at+38])
  assert after[:30]==before[:30] and after[30:]==[63,16,4,15]+ns['BODY'][var]+[0]
  assert m.get('S2PaletteAck')==[0,3,2,1][var] and m.get('VRAM_Buffer1_Offset')==37
  A.interrupt(m,0)
  assert list(m.vram[0x3f11:0x3f14])==ns['BODY'][var] and m.vram[0x3f00]==15
  rows.append(dict(variant=var,mode=mode,actual_WriteGameText_then_NMI_retry=True,complete_text_and_palette=after,actual_P0=list(m.vram[0x3f11:0x3f14]),BG=m.vram[0x3f00]))
 q['checks']['eight_actual_WriteGameText_published_ROM_retry']=rows
 verify();q['passed']=True
except Exception as e:
 q.update(error=repr(e),traceback=traceback.format_exc());raise
finally:
 paths={Path(__file__),P,H,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',Path(A.__file__),Path(M.__file__),Path(C.__file__)}
 paths|={p for p in[J/'source-stage.json',J.parent/'source-stage.json']if p.is_file()}
 q['bindings']={str(p.resolve()):sha(p)for p in sorted(paths)}
 out=O/'controls.json';out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(passed=q['passed'],path=str(out),sha256=sha(out))),flush=True)
