"""Keep both authentic DMC inputs: final127 clone plus original SMB2 samples.

V2 linked correct owned producers, then its metadata precondition wrongly
assumed every .incbin was final127. No source/cart defect or parent mutation.
"""
from pathlib import Path
p=Path(__file__).with_name('prepare_functional_roster_coherent62_v2.py');ns={'__file__':str(p),'__name__':'prepare_only'}
t=p.read_text().replace("exec(compile(s,__file__,'exec'),globals())",'');exec(compile(t,str(p),'exec'),ns)
s=ns['s'].replace('functional-roster-coherent62-v2','functional-roster-coherent62-v3')
a="paths=re.findall(r'\\.incbin \"([^\"]+)\"',old);assert len(set(paths))==1,paths\n write(J/'dmc-clones.s',old.replace(paths[0],(J/'final127.bin').as_posix()))"
b="paths=re.findall(r'\\.incbin \"([^\"]+)\"',old);clones={p for p in paths if Path(p).name=='final127.bin'};assert len(clones)==1 and len(set(paths))==2,paths\n write(J/'dmc-clones.s',old.replace(next(iter(clones)),(J/'final127.bin').as_posix()))"
assert s.count(a)==1;s=s.replace(a,b)
exec(compile(s,__file__,'exec'),globals())
