"""Additive source2.02 Bill rotation/end atlas. Every original record roundtrips.
Input hashes pin the existing remaining atlas; seven unrelated generators stay frozen.
"""
from pathlib import Path
import sys,json,re,math,hashlib,xml.etree.ElementTree as ET
from PIL import Image
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--reference-root',type=Path)
parser.add_argument('--inputs',type=Path,default=Path(__file__).resolve().parent/'bill_advanced_art_inputs')
parser.add_argument('--helpers-root',type=Path)
parser.add_argument('--baseline-provided',action='store_true',help='Use hash-pinned existing old outputs rather than regenerating them first.')
args=parser.parse_args();S=args.root.resolve();R=(args.reference_root or S).resolve();I=args.inputs.resolve()
REPORT=S/'build/bill-advanced-art.json';REPORT.parent.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,str(args.helpers_root or S/'tools/reference'));import build_remaining_art as old
if not args.baseline_provided:old.main()
manifest=json.loads((I/'manifest.json').read_text())
for n,d in manifest.items():assert sha(I/n)==d and sha(S/n)==d,(n,'Frozen input changed')
from prepare_crossover import frames
free=[0,1,13,14,15,21,25,27,28,29,30,31];text=(I/'src/remaining_art.inc').read_text();ids=(I/'src/remaining_art_ids.inc').read_text();fams=list(map(int,re.search(r'AvArtFamilies:\s*\.byte ([^\n]+)',text)[1].split(',')))
def banks(mp):
 a=[(I/f'chr/characters/samus-remaining-shared-{mp}.chr').read_bytes(),(I/f'chr/characters/special-remaining-shared-{mp}.chr').read_bytes()];v=(I/f'chr/characters/remaining-weapons-{mp}.chr').read_bytes();return a+[v[j:j+2048]for j in range(0,len(v),2048)]
original={mp:banks(mp)for mp in['mmc3','mmc5']};b=original['mmc3'];records=[]
pattern=r'AvArt(\d+)(Right|Left):\n \.byte (\d+)\n((?: \.byte [^\n]+\n)*)'
for i in range(len(fams)):
 sides=[]
 for side in['Right','Left']:
  m=re.search(r'AvArt'+str(i)+side+r':\n \.byte (\d+)\n((?: \.byte [^\n]+\n)*)',text);assert m
  parts=[]
  for line in m[2].splitlines():
   p=re.fullmatch(r' \.byte MetaspriteVramOffset\{\$([0-9a-f]+)\}, \{SPRITE_BANK_4\}, \$([0-9a-f]+), (-?\d+), (-?\d+)',line);assert p,line;tile,attr,y,x=[int(v,16)if j<2 else int(v)for j,v in enumerate(p.groups())];raw=b[fams[i]][1024+tile//2*32:1024+(tile//2+1)*32];parts.append((raw,attr,y,x))
  assert len(parts)*4==int(m[1]);sides.append(parts)
 records.append(sides)
old_records=[list(map(list,r))for r in records];newfams=fams[:]
for i,f in {1:15,2:15,24:12,79:13,80:12,81:12,82:12,83:13,84:13,90:0,91:13,92:0,93:13,94:0}.items():newfams[i]=f
items=list(ET.parse(R/'reference/crossover2/main.xml').getroot().iter('item'));sprite=next(i for i in items if i.get('type')=='DefineSpriteTag'and i.get('spriteId')=='166');sheet=Image.open(next((R/'reference/crossover2/images').glob('*_Bill000.png'))).convert('RGBA');pictures=old.extract(frames(sprite),144,sheet)
def rotate(pic,deg):
 out=Image.new('RGBA',pic.size);a=math.radians(deg);co,si=math.cos(a),math.sin(a)
 for y in range(96):
  for x in range(96):
   wx,wy=x+.5-48,y+.5-48;sx=math.floor(co*wx+si*wy+48);sy=math.floor(-si*wx+co*wy+48)
   if 0<=sx<96 and 0<=sy<96:out.putpixel((x,y),pic.getpixel((sx,sy)))
 return out
def parts(pic):
 def layers(im,projectile=False):
  out={2:[[0]*96 for _ in range(96)]}
  for y in range(96):
   for x in range(96):
    v=im.getpixel((x,y))
    if v[3]>=128:out[2][y][x]=1+min(range(3),key=lambda c:sum((v[k]-old.PALS[2][c][k])**2 for k in range(3)))
  return out
 old.assets.layers=layers;raw=[];p=old.packing.parts(pic,(48,48),raw);result=[]
 for t,a,x,y in p:
  canonical,flags=min((old.flipped(raw[t//2],f),f)for f in[0,64,128,192]);result.append((canonical,a^flags,y,x))
 return result
assert parts(pictures[3])==records[1][0] and parts(pictures[4])==records[2][0],'Exact existing source Bill frames'
newmeta=[]
for name,ix,angle in [('LASER45',4,45),('LASER90',4,90),('LASER135',4,135),('END0',2,0),('END45',2,45),('END90',2,90),('END135',2,135)]:
 pic=rotate(pictures[ix],angle);right=parts(pic);left=[(v,a^64,y,-x-8)for v,a,y,x in right];i=len(records);records.append([right,left]);newfams.append(15);ids+=f'AV_ART_BILL{name}={i}\n';newmeta.append({'name':name,'id':i,'source_frame':ix+1,'rotation':angle,'RGBA_sha256':hashlib.sha256(pic.tobytes()).hexdigest()})
# Preserve native shared prefixes and every unaffected tile/metadata record.
pools=[{}for _ in b]
for f in[0,1]:
 for slot in free[:5 if f==0 else 8]:pools[f][slot]=b[f][1024+slot*32:1024+(slot+1)*32]
for i,(f,rec)in enumerate(zip(newfams,records)):
 for v,a,y,x in rec[0]:
  if v in pools[f].values():continue
  oldslot=next((p for p in free if b[f][1024+p*32:1024+(p+1)*32]==v and p not in pools[f]),None)
  slot=oldslot if oldslot is not None else next((p for p in free if p not in pools[f]),None);assert slot is not None,(i,f,len(pools[f]));pools[f][slot]=v
assert len(pools[15])==11
newtext=text
for i in range(len(fams)):
 for side,parts0 in zip(['Right','Left'],records[i]):
  def emitted():
   lines=[f'AvArt{i}{side}:',f' .byte {len(parts0)*4}']
   for v,a,y,x in parts0:
    slot=next(p for p,value in pools[newfams[i]].items()if value==v);lines.append(f' .byte MetaspriteVramOffset{{${slot*2:02x}}}, {{SPRITE_BANK_4}}, ${a:02x}, {y}, {x}')
   return '\n'.join(lines)+'\n'
  pat=r'AvArt'+str(i)+side+r':\n \.byte \d+\n(?: \.byte [^\n]+\n)*';newtext,n=re.subn(pat,lambda _:emitted(),newtext);assert n==1
addition=['.segment "LINK_GFX"']
for i in range(len(fams),len(records)):
 for side,parts0 in zip(['Right','Left'],records[i]):
  addition +=[f'AvArt{i}{side}:',f' .byte {len(parts0)*4}']
  for v,a,y,x in parts0:
   slot=next(p for p,value in pools[15].items()if value==v);addition.append(f' .byte MetaspriteVramOffset{{${slot*2:02x}}}, {{SPRITE_BANK_4}}, ${a:02x}, {y}, {x}')
newtext=newtext.replace('.segment "SPECIAL_ROSTER"','\n'.join(addition)+'\n.segment "SPECIAL_ROSTER"')
for side in['Right','Left']:
 for suffix,op in[('Lo','<'),('Hi','>')]:
  label='AvArt'+side+suffix;newtext=re.sub(label+r':\n \.byte [^\n]+',label+':\n .byte '+','.join(op+f'AvArt{i}{side}'for i in range(len(records))),newtext)
for label,vals in [('AvArtBanks',[f'.bank(AvArt{i}Right)'for i in range(len(records))]),('AvArtFamilies',list(map(str,newfams)))]:newtext=re.sub(label+r':\n \.byte [^\n]+',label+':\n .byte '+','.join(vals),newtext)
(S/'src/remaining_art.inc').write_text(newtext);(S/'src/remaining_art_ids.inc').write_text(ids)
changes=[]
for mp,oldbanks in original.items():
 newbanks=[]
 for f,bank in enumerate(oldbanks):
  new=bytearray(bank)
  if f in[0,12,13,15]:
   bg=(S/'chr/mmc5/bg_ground.chr').read_bytes()[2048:4096]
   for p in free:new[1024+p*32:1024+(p+1)*32]=pools[f].get(p,bg[1024+p*32:1024+(p+1)*32])
  else:assert all(bank[1024+p*32:1024+(p+1)*32]==v for p,v in pools[f].items()),f
  assert new[:1024]==bank[:1024]
  for p in range(32):
   if p not in free:assert new[1024+p*32:1024+(p+1)*32]==bank[1024+p*32:1024+(p+1)*32]
  newbanks.append(bytes(new))
 # Exact source canonical bytes, attributes and OAM order for all101 old records.
 for i in range(len(fams)):
  for side,partset in enumerate(records[i]):
   for j,(v,a,y,x)in enumerate(partset):assert (v,a,y,x)==tuple(old_records[i][side][j]);assert v in pools[newfams[i]].values()
 for name,data in [('samus-remaining-shared',newbanks[0]),('special-remaining-shared',newbanks[1]),('remaining-weapons',b''.join(newbanks[2:]))]:
  n=f'chr/characters/{name}-{mp}.chr';(S/n).write_bytes(data);changes.append({'path':n,'before':manifest[n],'after':sha(S/n),'changed_bytes':sum(a!=z for a,z in zip((I/n).read_bytes(),data))})
report={'scope':'Additive successor. Original art-measure/art-space and frozen C2 untouched. Exact101old source records retain canonical pixels, attributes, pivots and OAM order, with bounded family repack. All SophiaExplosion records remain family16. Source rotation nearest pixel-center projection follows existing atlas extraction/quantizer convention, not an external Flash renderer comparison.','inputs':manifest,'moves':{str(i):[a,z]for i,(a,z)in enumerate(zip(fams,newfams))if a!=z},'pools':{str(f):len(v)for f,v in enumerate(pools)},'new':newmeta,'CHR':changes,'old_record_sides_proven':202,'old_OAM_parts_proven':sum(len(p)for r in old_records for p in r)}
REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
