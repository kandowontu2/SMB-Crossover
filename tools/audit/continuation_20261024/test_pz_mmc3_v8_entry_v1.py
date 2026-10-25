from pathlib import Path
import sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
original=R/'tools/audit/check_mmc3_oversized.py';t=original.read_text();a="(R/'build/oversized-mmc3-nf/source/chr/characters/oversized-raw.chr').as_posix()";assert t.count(a)==1
p=D/'ryu-head-oversized-mmc3-v8/source/chr/characters/oversized-raw.chr';t=t.replace(a,repr(p.as_posix()))
ns={'__file__':str(original),'__name__':'_private_cold'};exec(compile(t,str(original),'exec'),ns)
sys.argv=[str(original),'--rom',str(D/'ryu-head-oversized-mmc3-v8/candidate.nes'),'--names','Mario','Zelda II Link','Sypha','--output',str(D/'ryu-head-oversized-mmc3-v8/entry-v1')]
raise SystemExit(ns['main']())
