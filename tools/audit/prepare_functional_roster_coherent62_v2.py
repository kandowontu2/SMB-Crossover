"""Bind FF replacements by real original object path, never basename.

V1 retained a link-only negative: Quick/stream.o and FF/stream.o share a
basename. No old output/source was written. This keeps genuine Quick stream
input and replaces ONLY actual FF producer objects.
"""
from pathlib import Path
p=Path(__file__).with_name('prepare_functional_roster_coherent62_v1.py');s=p.read_text()
s=s.replace("build/functional-roster-coherent62-v1'","build/functional-roster-coherent62-v2'")
a="if x.endswith('.o')and Path(x).stem in replace:link[i]=str(J/Path(x).name)"
b="if x==str(P/'joint/main.o')or x in [str(BASE/(n+'.o'))for n in names]:link[i]=str(J/Path(x).name)"
assert s.count(a)==1;s=s.replace(a,b)
exec(compile(s,__file__,'exec'),globals())
