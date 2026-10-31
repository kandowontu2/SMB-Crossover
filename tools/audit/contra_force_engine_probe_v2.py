"""Retain v1 unseeded original pair-shadow negative; seed genuine source36."""
from pathlib import Path
P=Path(__file__).with_name('contra_force_engine_probe_v1.py')
s=P.read_text().replace("O=R/'build/contra-force-engine-probe-v1'", "O=R/'build/contra-force-engine-probe-v2'")
s=s.replace('def pair(self,lo):self.reg[6:8]=[lo,lo+1];self.map()', 'def pair(self,lo):self.reg[6:8]=[lo,lo+1];self[0x36]=2 if lo==4 else 0;self.map()')
exec(compile(s,str(P),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})
