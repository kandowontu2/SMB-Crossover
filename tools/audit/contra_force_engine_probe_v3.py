"""Retain v2 wrong actor-array inventory; inspect genuine0682 projectile slots."""
from pathlib import Path
P=Path(__file__).with_name('contra_force_engine_probe_v1.py')
s=P.read_text().replace("O=R/'build/contra-force-engine-probe-v1'", "O=R/'build/contra-force-engine-probe-v3'")
s=s.replace('def pair(self,lo):self.reg[6:8]=[lo,lo+1];self.map()', 'def pair(self,lo):self.reg[6:8]=[lo,lo+1];self[0x36]=2 if lo==4 else 0;self.map()')
s=s.replace('m[0x782]=1;', 'm[0x782]=0x2e;')
s=s.replace("kind=m[0x782+i]", "kind=m[0x682+i]")
s=s.replace("for i in range(2,10)if m[0x782+i]", "for i in range(2,26)if m[0x682+i]")
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
