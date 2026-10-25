"""Stage complete Bass source poses while preserving the existing walk artwork.

Only the three body clips whose forward arm is separate are replaced. Native
walk, directional firing, hurt and special poses retain their prior pixels.
The E1 bank is pinned for the optimized WALK3 descriptor, and pair0 remains the
common buster in every normal body bank. No mapper capacity is added.
"""
from pathlib import Path
import sys,json,re,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
import build_expanded_assets as a,build_samus_assets as packing
from build_ordinary_body_layout import source_parts
O=R/'build/verification/new-roster-1-1-nd/bass-arm-build-v3';O.mkdir(exist_ok=False)
source=R/'src/bass_metasprites.inc';code=source.read_text();plan=json.loads((O.parent/'bass-arm-optimized/plan.json').read_text())
def table(n):return[v.strip()for v in re.search(r'^'+n+r':\n\s+\.byte ([^\n]+)',code,re.M)[1].split(',')]
banks=[int(v[1:],16)for v in table('XgBASSBanks')];refs=[s.lstrip('<>')for s in table('XgBASSRightLo')]
aliases=dict(re.findall(r'^(\w+) = (\w+)$',code,re.M))
def resolve(n):
 while n in aliases:n=aliases[n]
 return n
first=0xd1+len((R/'chr/characters/crossover-roster-high.chr').read_bytes())//1024
blob=(R/'chr/characters/crossover-expanded.chr').read_bytes()
blocks={b:blob[(b-first)*1024:(b-first+1)*1024]for b in range(224,231)}
jobs={};owners={}
for name,b in zip(refs,banks):
 label=resolve(name);owners.setdefault(label,set()).add(b)
 if b==0x82:continue
 ps=source_parts(source,label)
 patterns=[blocks[b][i*32:(i+1)*32]for i in range(32)]
 raw=[(patterns[p['tile']//2],p['a'],p['x'],p['y'])for p in ps]
 if label in jobs:assert jobs[label]==raw,(label,b)
 jobs[label]=raw
for label in list(jobs):
 if 0x82 in owners[label]:del jobs[label]
changed=[]
for item in plan['jobs']:
 label=resolve('XgBASS0_'+item['pose']+'Right');pats=[bytes.fromhex(v)for v in item['patterns']]
 jobs[label]=[(pats[t//2],at,x,y)for t,at,x,y in item['parts']];changed.append(label)
groups={b:[blocks[b][i*32:(i+1)*32]for i in range(32)]if b==225 else[blocks[b][:32]]for b in blocks}
# Pin the exact E1 bank, including optimized WALK3's extra pair30. Unused holes
# can receive new records without affecting any old source record.
live={b:({0}if b!=225 else set(plan['used'][str(b)]))for b in blocks}
assignment={};records={}
for label in sorted(jobs,key=lambda n:-len(set(p[0]for p in jobs[n]))):
 need=set(p[0]for p in jobs[label]);choices=[]
 for b,g in groups.items():
  present={g[i]for i in live[b]};extra=need-present
  if b==225 and len(extra)>32-len(live[b]):continue
  if b!=225 and len(g)+len(extra)>32:continue
  choices.append((len(extra),b not in owners[label],len(live[b]),b))
 assert choices,('Normal Bass needs more than its seven existing banks',label)
 b=min(choices)[-1];assignment[label]=b;g=groups[b]
 for pattern in dict.fromkeys(p[0]for p in jobs[label]):
  if any(g[i]==pattern for i in live[b]):continue
  if b==225:i=min(set(range(32))-live[b]);g[i]=pattern
  else:i=len(g);g.append(pattern)
  live[b].add(i)
 records[label]=[(next(i for i in live[b]if g[i]==pat)*2,at,x,y)for pat,at,x,y in jobs[label]]
result=bytearray(blob)
for b,g in groups.items():
 data=b''.join(g)+bytes(1024-len(g)*32);assert data[:32]==blocks[b][:32]
 if b==225:
  assert all(data[i*32:(i+1)*32]==blocks[b][i*32:(i+1)*32]for i in plan['used'][str(b)])
 result[(b-first)*1024:(b-first+1)*1024]=data
# Retain all original labels/aliases/tables; change only record bytes and bank
# entries that now refer to those records. This avoids reordering unrelated art.
for label,ps in records.items():
 root=label.removesuffix('Right')
 for side in('Left','Right'):
  name=root+side
  if not re.search(r'^'+name+r':$',code,re.M):continue
  lines=[]
  for t,at,x,y in ps:
   if side=='Left':x=8-x;at^=64
   lines.append(f'  .byte MetaspriteVramOffset{{$%02x}}, {{SPRITE_BANK_0}}, $%02x, %d, %d'%(t,at,y,x))
  replacement=name+':\n  .byte '+str(len(ps)*4)+'\n'+'\n'.join(lines)+'\n'
  code,n=re.subn(r'^'+name+r':\n.*?(?=^[A-Za-z_.]|\Z)',replacement,code,count=1,flags=re.M|re.S);assert n==1,name
newbanks=[assignment.get(resolve(n),b)for n,b in zip(refs,banks)]
code,n=re.subn(r'(^XgBASSBanks:\n\s+\.byte )[^\n]+',lambda m:m[1]+','.join(f'${b:02x}'for b in newbanks),code,flags=re.M);assert n==1
overlay=O/'overlay';(overlay/'src').mkdir(parents=True);(overlay/'chr/characters').mkdir(parents=True)
(overlay/'src/bass_metasprites.inc').write_text(code)
(overlay/'chr/characters/crossover-expanded.chr').write_bytes(result)
manifest={'changed_source_clips':changed,'used_pairs':{b:len(v)for b,v in live.items()},'new_banks':0,'preserved_walk1_private_bank':True,'pinned_walk3_pairs':plan['used']['225'],'before_sha256':hashlib.sha256(blob).hexdigest(),'after_sha256':hashlib.sha256(result).hexdigest(),'assignments':assignment}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
