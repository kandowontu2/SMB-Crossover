from pathlib import Path
import re,json
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
for name in ('roll_art.inc','roll_world_art.inc','parodius_art.inc','parodius_death_art.inc','parodius_extra_art.inc'):
 p=R/'src'/name
 if not p.exists():continue
 vals=[]
 for m in re.finditer(r'(^[A-Za-z_][A-Za-z_0-9]*:\s*)(\.byte [^\n]+\n(?:[ \t]*\.byte [^\n]+\n)*)',p.read_text(),re.M):
  try:a=[int(v.strip().replace('$','0x'),0)for line in m[2].splitlines()for v in line.split('.byte',1)[1].split(',')]
  except (ValueError,IndexError):continue
  if a and a[0]%4==0 and len(a)==a[0]+1:vals+=a[1::4]
 print(json.dumps(dict(file=name,parts=len(vals),odd=sorted(set(v for v in vals if v&1)),even_min=min([v for v in vals if not v&1],default=-1),even_max=max([v for v in vals if not v&1],default=-1))))
