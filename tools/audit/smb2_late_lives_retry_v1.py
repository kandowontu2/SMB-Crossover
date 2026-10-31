"""Actual native WriteGameText cold deferred-ROM palette retry consumer."""
from pathlib import Path
import hashlib,json,itertools
R=Path(__file__).resolve().parents[2];P=Path(__file__).with_name('smb2_late_lives_controls_v1.py');s=P.read_text(encoding='utf-8').split('def main():',1)[0].replace("J=R/'build/smb2-late-lives-palette-v4/joint'","J=R/'build/smb2-late-lives-palette-v6/joint'")
ns={'__file__':str(P),'__name__':'_one_late_retry_source'};exec(compile(s,str(P),'exec'),ns);A,C,M,J=map(ns.get,['A','C','M','J']);O=R/'build/smb2-late-lives-retry-v1';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rows=[]
for var,mode in itertools.product(range(4),range(2)):
 m=ns['seed'](J,var,mode);M.put(m,OperMode=1,ScreenRoutineTask=6,BackgroundColorCtrl=0,VRAM_Buffer1_Offset=83,VRAM_Buffer_AddrCtrl=3,S2PaletteAck=0)
 z=C.invoke(m,'WriteGameText',A=1);assert m.get('S2PaletteAck')==255 and m.get('VRAM_Buffer1_Offset')==30
 at=m.lab['VRAM_Buffer1'];before=list(m.ram[at:at+31]);A.interrupt(m,0);assert m.get('VRAM_Buffer_AddrCtrl')==0
 z=C.invoke(m,'WriteGameText',A=1);after=list(m.ram[at:at+38]);assert after[:30]==before[:30]and after[30:]==[63,16,4,15]+ns['BODY'][var]+[0]and m.get('S2PaletteAck')==[0,3,2,1][var]and m.get('VRAM_Buffer1_Offset')==37
 A.interrupt(m,0);assert list(m.vram[0x3f11:0x3f14])==ns['BODY'][var]and m.vram[0x3f00]==15
 rows.append(dict(variant=var,mode=mode,published_ROM_deferral_keeps_ACK_invalid=True,actual_WriteGameText_then_NMI_retry=True,complete_prefix_and_palette=after,actual_P0=list(m.vram[0x3f11:0x3f14]),BG=m.vram[0x3f00]))
paths={Path(__file__),P,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',Path(A.__file__),Path(M.__file__),Path(C.__file__)};p=O/'controls.json';p.write_text(json.dumps(dict(passed=True,native=False,cases=len(rows),rows=rows,bindings={str(p.resolve()):sha(p)for p in paths}),indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,cases=len(rows),path=str(p),sha256=sha(p))),flush=True)
