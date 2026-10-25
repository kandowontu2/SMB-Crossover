"""Compare every old/new Bass palette-symbol composite and capacity bound."""
from pathlib import Path
import sys,json,re,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
from build_ordinary_body_layout import source_parts,composite
from PIL import Image
O=R/'build/verification/new-roster-1-1-nd/bass-final-overlay-v3'
plan=json.loads((O.parent/'bass-arm-optimized/plan.json').read_text())
text=(R/'src/chr_map_mmc5.inc').read_text().split('ChrPhysicalMap:\n')[1].split('.popseg')[0]
mapping=[int(v)for l in text.splitlines()if'.byte'in l for v in l.split('.byte')[1].split(',')]
oldchr=(R/'chr/characters/packed-mmc5.chr').read_bytes();newchr=(O/'chr/characters/packed-mmc5.chr').read_bytes()
def read(path,prefix):
 text=path.read_text();aliases=dict(re.findall(r'^(\w+) = (\w+)$',text,re.M))
 def table(n):return[v.strip()for v in re.search(r'^'+n+r':\n\s+\.byte ([^\n]+)',text,re.M)[1].split(',')]
 banks=[int(v[1:],16)if v.startswith('$')else int(v)for v in table(prefix+'Banks')]
 def resolve(n):
  while n in aliases:n=aliases[n]
  return n
 data={}
 for side in('Left','Right'):
  for i,(name,bank)in enumerate(zip(table(prefix+side+'Lo'),banks)):
   name=name.lstrip('<>');label=resolve(name);ps=source_parts(path,label)
   data[i,side]=(name,label,bank,ps)
 return data
def pixels(parts,bank,raw):return composite(parts,raw[mapping[bank]*1024:(mapping[bank]+1)*1024])
def planned(item,side):
 raw=b''.join(bytes.fromhex(v)for v in item['patterns']);ps=[]
 for t,a,x,y in item['parts']:
  if side=='Left':x=8-x;a^=64
  ps.append(dict(tile=t,a=a,x=x,y=y))
 return composite(ps,raw)
replacements={p['pose']:p for p in plan['jobs']};reports={}
for filename,prefix in(('bass_metasprites.inc','XgBASS'),('bass_special_poses.inc','SsBass')):
 old=read(R/'src'/filename,prefix);new=read(O/'src'/filename,prefix);assert old.keys()==new.keys();changed=preserved=0;peaks={}
 for key,(name,label,bank,ps)in old.items():
  nn,nl,nb,np=new[key];assert name==nn
  before=pixels(ps,bank,oldchr);after=pixels(np,nb,newchr)
  if before==after:preserved+=1;continue
  changed+=1
  if prefix=='XgBASS':
   pose=next((p for p in replacements if label=='XgBASS0_'+p+'Right'.replace('Right',key[1])),None)
   assert pose,(name,label)
   assert after==planned(replacements[pose],key[1]),('Exact source composite',name)
  else:
   pose=next((p for p in replacements if label=='SsBassPHARAOH_'+p+key[1]),None)
   assert pose,(name,label)
   pic=Image.open(O.parent/'bass-arm-plan'/(pose+'.png')).convert('RGBA')
   colors=[((5,5,5),(3,1)),((112,112,112),(2,3)),((248,152,56),(2,2)),((248,224,160),(3,2)),((255,255,255),(2,2))]
   expected=[]
   for y in range(pic.height):
    for x in range(pic.width):
     v=pic.getpixel((x,y))
     if v[3]<128:continue
     p,c=min(colors,key=lambda z:sum((v[k]-z[0][k])**2 for k in range(3)))[1]
     px=x-32;py=y-32
     if key[1]=='Left':px=15-px
     expected.append([px,py,p,c])
   assert sorted(expected)==after,('Exact Pharaoh source composite',name)
  visible=[p for p in np if not p['a']&4]
  peak=max(sum(p['y']<=s<p['y']+16 for p in visible)for s in range(-32,65))
  peaks[name]=peak
 assert changed>0 and preserved>40
 reports[filename]=dict(changed_source_composites=changed,preserved_other_composites=preserved,default_outline_off_peaks=peaks)
(O.parent/'bass-composite-proof.json').write_text(json.dumps(reports,indent=2)+'\n');print(json.dumps({n:{k:v for k,v in d.items()if k!='default_outline_off_peaks'}for n,d in reports.items()}))
