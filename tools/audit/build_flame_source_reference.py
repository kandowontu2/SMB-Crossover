"""Pin Flame Blast color pixels directly from the archived 2.02 SWF masks.

This oracle never reads generated CHR, metasprite packing, or runtime art tables.
The fixed palette is justified by GraphicsManager's suit-color rectangles, which
exclude the projectile sheet region used by frames24..39.
"""
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from build_special_art import extract,RGB
from prepare_crossover import frames

def main():
 source=ROOT/'reference/crossover2'
 provenance=json.loads((source/'source.json').read_text())
 assert hashlib.sha256((source/'source.swf').read_bytes()).hexdigest()==provenance['sha256']
 tree=ET.parse(source/'main.xml');items=list(tree.getroot().iter('item'));symbols={}
 for tag in items:
  if tag.get('type') in ('SymbolClassTag','ExportAssetsTag'):
   ids,names=tag.find('tags'),tag.find('names')
   if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
 sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
 paths=[source/'images'/n for n in ('625_com.smbc.graphics.skins.BmdInfo_MegaMan000.png','412_com.smbc.graphics.skins.BmdInfo_Bass000.png')]
 timeline=frames(sprites[symbols['MegaManProjectile']])
 images=[extract(timeline,24,Image.open(p).convert('RGBA')) for p in paths]
 manager=source/'extracted/scripts/com/smbc/managers/GraphicsManager.as'
 line=next(s for s in manager.read_text().splitlines()if 'ai(megaManNum,MegaManBase.IND_CI_MegaManSuitColors,'in s)
 recolors=[list(map(int,v))for v in re.findall(r'ar\((\d+),(\d+),(\d+),(\d+)\)',line)]
 assert len(recolors)==4
 regions=[]
 for index,frame in enumerate(timeline,1):
  if index not in range(24,40):continue
  entries=sorted(frame['display'].items(),key=lambda p:int(p[0]))
  for i,(_,v)in enumerate(entries):
   if v.get('characterId')!='24':continue
   mask=next((v for _,v in entries[i+1:]if v.get('characterId')=='18'),None)
   if not mask:continue
   m,mm=v['matrix'],mask['matrix'];x,y=(float(mm[k])/40 for k in('translateX','translateY'));w,h=(float(mm[k])/2 for k in('scaleX','scaleY'))
   left=x-float(m['translateX'])/40;top=y-float(m['translateY'])/40
   rect=[round(left),round(top),round(w),round(h)]
   for a,b,c,d in recolors:assert not(left<a+c and left+w>a and top<b+d and top+h>b),(index,rect,[a,b,c,d])
   regions.append(dict(frame=index,rect=rect))
 assert len(regions)==16
 colors=[(0x0f,RGB[0x0f],'b'),(0x16,RGB[0x16],'r'),(0x27,RGB[0x27],'o')]
 records={}
 for angle,first,start in ((0,22,24),(90,70,25),(180,85,25),(270,100,25)):
  for index in range(start,40):
   im=images[0][index-1];assert im.tobytes()==images[1][index-1].tobytes(),index
   if angle:im=im.rotate(-angle,center=(48,48),resample=Image.Resampling.NEAREST)
   bbox=im.getbbox();x0,y0,x1,y1=bbox
   rows=[]
   for y in range(y0,y1):
    row=''
    for x in range(x0,x1):
     v=im.getpixel((x,y));row += '.' if v[3]<128 else min(colors,key=lambda z:sum((v[k]-z[1][k])**2 for k in range(3)))[2]
    rows.append(row)
   records[first+index-start]=dict(x=x0-48,y=y0-48,rows=rows)
 out=['-- Independent raw SWF bitmap/mask pixels; no generated CHR/metasprite input.',f'-- SWF SHA256 {provenance["sha256"]}','return {']
 for art,p in records.items():out.append('[%d]={x=%d,y=%d,rows={%s}},'%(art,p['x'],p['y'],','.join(json.dumps(s) for s in p['rows'])))
 out.append('}')
 path=ROOT/'tests/fixtures/flame-source-pixels.lua';path.write_text('\n'.join(out)+'\n')
 report=dict(swf_sha256=provenance['sha256'],images={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},frames=len(records),colors={'b':15,'r':22,'o':39},suit_recolor_rectangles=recolors,suit_recolor_source_sha256=hashlib.sha256(manager.read_bytes()).hexdigest(),source_flame_regions=regions,oracle_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 (ROOT/'tests/fixtures/flame-source-pixels.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Pinned',len(records),'source Flame frames; bytes',path.stat().st_size)
if __name__=='__main__':main()
