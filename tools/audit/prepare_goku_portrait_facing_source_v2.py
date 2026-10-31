"""Retarget linker passthrough outputs explicitly; retain v1 guard rejection."""
from pathlib import Path
p=Path(__file__).with_name('prepare_goku_portrait_facing_source_v1.py');s=p.read_text()
s=s.replace("build/goku-portrait-facing-source-v1'","build/goku-portrait-facing-source-v2'")
anchor=" assert str(O/'dp-component.o')in link"
replacement=""" if '--ld-args' in link:
  k=link.index('--ld-args')+1;v=link[k].split(',')
  for j in range(1,len(v),2):v[j]=str(O/Path(v[j]).name)
  link[k]=','.join(v)
"""+anchor
assert s.count(anchor)==1;s=s.replace(anchor,replacement)
exec(compile(s,__file__,'exec'),globals())
