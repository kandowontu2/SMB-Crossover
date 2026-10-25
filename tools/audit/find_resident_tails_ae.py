from pathlib import Path
import re
R=Path(__file__).resolve().parents[2]
for p in (R/'src').glob('*.s'):
 segment=None;stack=[];previous=None
 for n,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
  s=line.split(';')[0].strip()
  if not s:continue
  if s=='.pushseg':stack.append(segment)
  elif s=='.popseg':segment=stack.pop()if stack else None
  elif (m:=re.match(r'\.segment "([^"]+)"',s)):segment=m[1]
  if s=='rts'and previous and previous[1].startswith('jsr ')and segment in ('CODE','LOWCODE','COLLISION'):
   print(p.relative_to(R),previous[0],segment,previous[1])
  previous=n,s
