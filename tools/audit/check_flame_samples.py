"""Compare completed-DMA flame samples to pinned SWF pixels, not CHR packing."""
from pathlib import Path
import sys,re,struct,json,xml.etree.ElementTree as ET
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/reference'))
from build_special_art import extract,RGB
from prepare_crossover import frames

def main():
 tree=ET.parse(ROOT/'reference/crossover2/main.xml');items=list(tree.getroot().iter('item'));symbols={}
 for tag in items:
  if tag.get('type') in ('SymbolClassTag','ExportAssetsTag'):
   ids=tag.find('tags');names=tag.find('names')
   if ids is not None and names is not None:symbols.update({n.text:i.text for i,n in zip(ids,names)})
 sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
 sheet=Image.open(ROOT/'reference/crossover2/images/625_com.smbc.graphics.skins.BmdInfo_MegaMan000.png').convert('RGBA')
 images=extract(frames(sprites[symbols['MegaManProjectile']]),24,sheet)
 # Four distinct original colors; no metasprite/tile/pool algorithm enters this oracle.
 colors=[(i,RGB[i]) for i in (0x0f,0x16,0x27,0x30)]
 report={}
 for mapper in ('mmc3','mmc5'):
  base=ROOT/f'build/verification/smb-crossover-{mapper}-flame'
  lines=base.with_name(base.name+'-samples.lua').read_text().splitlines()[1:-1]
  raw=base.with_name(base.name+'-dma.bin').read_bytes();size=10536
  assert len(raw)==len(lines)*size,(len(raw),len(lines),size)
  cases=[]
  for n,line in enumerate(lines):
   head={k:int(v) for k,v in re.findall(r'(frame|phase|screen)=(-?\d+)',line.split('parts={')[0])}
   parts=[{k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',s)} for s in re.findall(r'\{([^{}]+)\}',line.split('parts={')[1].split('},shots=')[0])]
   shots={int(i):{k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',s)} for i,s in re.findall(r'\[(\d+)\]=\{([^{}]+)\}',line.split('shots={')[1])}
   rec=raw[n*size:(n+1)*size];frame,ce,oe=struct.unpack('<IHH',rec[:8]);assert frame==head['frame']
   oam=rec[8:264];chrdata=rec[264:8456];palette=rec[10504:10536]
   for slot in sorted(set(p['slot'] for p in parts)):
    shot=shots[slot];art=shot['art']
    if not 23<=art<=37:continue
    ox=shot['x']-head['screen'];oy=shot['y']+1
    actual={}
    for p in sorted([p for p in parts if p['slot']==slot],key=lambda p:p['o'],reverse=True):
     y,t,a,x=oam[p['o']:p['o']+4];y+=1
     address=(t&1)*4096+(t&254)*16
     for dy in range(16):
      row=15-dy if a&128 else dy
      for dx in range(8):
       bit=dx if a&64 else 7-dx
       off=address+(row//8)*16+row%8
       color=((chrdata[off]>>bit)&1)+2*((chrdata[off+8]>>bit)&1)
       if color:actual[(x+dx-ox,y+dy-oy)]=palette[16+(a&3)*4+color]&63
    im=images[art+1]
    ref={(x-48,y-48):min(colors,key=lambda c:sum((im.getpixel((x,y))[k]-c[1][k])**2 for k in range(3)))[0]
      for y in range(96) for x in range(96) if im.getpixel((x,y))[3]>=128}
    keys=set(actual)|set(ref);errors=sum(actual.get(k)!=ref.get(k) for k in keys)
    cases.append(dict(frame=frame,art=art,slot=slot,pixels=len(ref),errors=errors,actual_colors=sorted(set(actual.values())),expected_colors=sorted(set(ref.values()))))
    if errors and n<4:
     for name,pic in [('source',ref),('actual',actual)]:
      out=Image.new('RGBA',(96,96))
      for (x,y),v in pic.items():
       if 0<=x+48<96 and 0<=y+48<96:out.putpixel((x+48,y+48),RGB.get(v,(255,0,255))+(255,))
      out.save(ROOT/f'build/verification/{mapper}-flame-{art}-{name}.png')
  report[mapper]=dict(cases=cases,total_errors=sum(c['errors'] for c in cases))
 (ROOT/'build/verification/flame-source-pixel-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n')
 for mapper,rec in report.items():print(mapper,len(rec['cases']),'source-pixel comparisons;',rec['total_errors'],'errors',rec['cases'][:3])

if __name__=='__main__':main()
