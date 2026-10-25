from pathlib import Path
import sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
f=R/'tools/audit/check_mmc3_oversized.py';t=f.read_text();a="(R/'build/oversized-mmc3-nf/source/chr/characters/oversized-raw.chr').as_posix()";assert t.count(a)==1;t=t.replace(a,repr((D/'ryu-head-oversized-mmc3-v11/source/chr/characters/oversized-raw.chr').as_posix()))
a=" cases.append(('Meta Knight',12,13,'KbVariant',1))";assert t.count(a)==1;t=t.replace(a,a+"\n cases += [('Roll',9,9,'RlVariant',1),('Octopus',17,18,'VvVariant',1),('TwinBee',17,18,'VvVariant',2),('Pentarou',17,18,'VvVariant',3)]")
ns={'__file__':str(f),'__name__':'_private_cold37'};exec(compile(t,str(f),'exec'),ns)
sys.argv=[str(f),'--rom',str(D/'ryu-head-oversized-mmc3-v11/candidate.nes'),'--output',str(D/'ryu-head-oversized-mmc3-v11/entry-v1')]
raise SystemExit(ns['main']())
