"""Successor controls retain v1 SFC-observable mismatch, bind corrected actual code."""
from pathlib import Path
P=Path(__file__).with_name('smb2_late_lives_controls_v1.py');s=P.read_text(encoding='utf-8')
s=s.replace('build/smb2-late-lives-controls-v1','build/smb2-late-lives-controls-v2').replace('build/smb2-late-lives-palette-v4','build/smb2-late-lives-palette-v6').replace('6c6ad55fb77b3ad1741440557541342a2829c971f65e2be92f492ec741ff88fe','f3a2c5a391b50545b98b345cbff2d767e53a8ca8c1404650a95a80a7cbb8dd37')
s=s.replace('  abi=[]\n','  apiSeeds={j:seed(j)for j in[P,J]};abi=[]\n')
s=s.replace("m=seed(j);M.put(m,VRAM_Buffer1_Offset=0", "m=copy.deepcopy(apiSeeds[j]);M.put(m,VRAM_Buffer1_Offset=0")
s=s.replace('m=seed(J,var);M.put(m,OperMode=1','m=copy.deepcopy(bases[var]);M.put(m,OperMode=1')
s=s.replace("assert z['registers']==dict(A=1,X=0x57,Y=30,P=p)and", "control=copy.deepcopy(apiSeeds[P]);reference=C.invoke(control,'S2MenuStatus',A=1,X=0x57,Y=30,P=p);assert bytes(m.ram[0x15a:0x17b])==bytes(control.ram[0x15a:0x17b]);assert z['registers']==reference['registers']and")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
