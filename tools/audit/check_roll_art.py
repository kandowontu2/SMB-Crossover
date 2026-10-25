"""Independent source-pixel check of both facings and outline settings."""
from pathlib import Path
import argparse,json,hashlib,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--output',type=Path,default=ROOT/'build/verification/roll-art-proof.json')
 p.add_argument('--previous-source',type=Path,help='Also preserve every visible pixel from a saved source bundle, including the outlines-off mask policy')
 args=p.parse_args()
 m=json.loads((ROOT/'reference/roll-mobile/art.json').read_text());chr=(ROOT/'chr/characters/roll.chr').read_bytes()
 previous=None
 if args.previous_source:
  with zipfile.ZipFile(args.previous_source)as z:
   previous=(json.loads(z.read('reference/roll-mobile/art.json')),z.read('chr/characters/roll.chr'))
 s=Image.open(ROOT/'reference/new-roster-art/rollsheet_mobile1.png').convert('RGBA')
 assert hashlib.sha256(chr).hexdigest()==m['CHR_sha256']
 colors={(8,8,8):15,(248,184,0):40,(248,56,0):22,(248,224,168):55,(0,168,0):26,(248,248,248):48,(168,16,0):23}
 cases=[];shot_cases=[]
 for f,(_,box,anchor)in enumerate(m['frames']):
  for outline in(0,1):
   for facing in(1,2):
    expected={}
    for y in range(box[1],box[3]):
     for x in range(box[0],box[2]):
      rgba=s.getpixel((x,y))
      if rgba[3]:
       dx=x-anchor[0]+8;dy=y-anchor[1]+32
       expected[(dx if facing==1 else 15-dx,dy)]=colors[rgba[:3]]
    pool=m['pool_for'][str(f)];actual={}
    for tile,attr,dy,dx in reversed(m['records'][f'{f}-{outline}-{facing}']):
     dx=dx if dx<128 else dx-256;dy=dy if dy<128 else dy-256
     offset=pool*4096+(2048 if tile&1 else 0)+(tile&62)*16;data=chr[offset:offset+32]
     for y in range(16):
      for x in range(8):
       sx=7-x if attr&64 else x;sy=15-y if attr&128 else y;i=(sy//8)*16+sy%8
       v=((data[i]>>(7-sx))&1)|(((data[i+8]>>(7-sx))&1)<<1)
       if v:actual[(dx+x,dy+y)]=m['palettes'][attr&3][v-1]
    assert all(expected.get(p)==v for p,v in actual.items()),(f,outline,facing,'invented/changed source pixels')
    missing=set(expected)-set(actual)
    assert not missing if outline else all(expected[p]==15 for p in missing),(f,outline,facing,'non-ink source pixels missing')
    if previous:
     old,old_chr=previous;old_actual={};old_pool=old['pool_for'][str(f)]
     for tile,attr,dy,dx in reversed(old['records'][f'{f}-{outline}-{facing}']):
      dx=dx if dx<128 else dx-256;dy=dy if dy<128 else dy-256
      offset=old_pool*4096+(2048 if tile&1 else 0)+(tile&62)*16;data=old_chr[offset:offset+32]
      for y in range(16):
       for x in range(8):
        sx=7-x if attr&64 else x;sy=15-y if attr&128 else y;i=(sy//8)*16+sy%8
        value=((data[i]>>(7-sx))&1)|(((data[i+8]>>(7-sx))&1)<<1)
        if value:old_actual[(dx+x,dy+y)]=old['palettes'][attr&3][value-1]
     assert actual==old_actual,(f,outline,facing,'Visible pixels changed from saved source bundle')
    cases.append(dict(frame=f,outline=outline,facing=facing,pixels=len(actual),omitted_optional_ink=len(missing)))
 shot_colors={**colors,(248,120,248):0x24,(248,184,248):0x30}
 for f,(name,box,anchor)in enumerate(m['shots']):
  for facing in(1,2):
   expected={}
   for y in range(box[1],box[3]):
    for x in range(box[0],box[2]):
     rgba=s.getpixel((x,y))
     if rgba[3]:
      dx=x-anchor[0];value=0x24 if name=='burst-pink'else 0x30 if name=='burst-white'else shot_colors[rgba[:3]]
      expected[(dx if facing==1 else -dx-1,y-anchor[1])]=value
   actual={};parts=m['shot_records'if facing==1 else 'shot_left_records'][f]
   if name.startswith('burst-'):assert len(parts)<=4,'Charge beam must leave scanline capacity for the player'
   for tile,attr,dy,dx in reversed(parts):
    dx=dx if dx<128 else dx-256;dy=dy if dy<128 else dy-256
    data=chr[3072+(tile&62)*16:3072+(tile&62)*16+32]
    for y in range(16):
     for x in range(8):
      sx=7-x if attr&64 else x;sy=15-y if attr&128 else y;i=(sy//8)*16+sy%8
      v=((data[i]>>(7-sx))&1)|(((data[i+8]>>(7-sx))&1)<<1)
      if v:actual[(dx+x,dy+y)]=m['palettes'][attr&3][v-1]
   assert actual==expected,(name,facing,'Source projectile/orb pixels differ',len(actual),len(expected))
   shot_cases.append(dict(name=name,facing=facing,pixels=len(actual)))
 out=args.output.resolve();out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(dict(source_sha256=m['source_sha256'],CHR_sha256=m['CHR_sha256'],cases=cases,shots=shot_cases,previous_source_sha256=hashlib.sha256(args.previous_source.read_bytes()).hexdigest()if previous else None,previous_body_pixels_identical=bool(previous),passed=True),indent=2)+'\n')
 print('PASS',len(cases),'source-pixel Roll poses and',len(shot_cases),'projectile/orb facings')
if __name__=='__main__':main()
