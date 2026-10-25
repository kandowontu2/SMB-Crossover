from pathlib import Path
import json,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,location
b=load(D/'mmc3-ship-lives-v25/candidate.nes');rows=[]
for n,s in b['syms'].items():
 if 'seg'not in s or'size'not in s:continue
 g=b['segs'][s['seg']]
 if'ooffs'not in g:continue
 size=int(s['size'],0);bank=(location(b,n)-16)//8192
 if bank in(254,255)and size>=42:rows.append(dict(name=n,bank=bank,address=int(s['val'],0),size=size,segment=g['name'].strip('"')))
rows.sort(key=lambda z:(z['bank'],z['size'],z['address']));(D/'mmc3-resident-scopes-v25.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[:28]),flush=True)
