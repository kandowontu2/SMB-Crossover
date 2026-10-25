"""Source TMNT1 equipment art; preserve all existing body/primary CHR bytes."""
from pathlib import Path
import hashlib,json,argparse
parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--source-chr',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();D=args.output;D.mkdir(parents=True,exist_ok=False);rom=args.reference.read_bytes();prg=rom[16:131088];chr=rom[131088:]
assert hashlib.sha256(rom).hexdigest()=='15e112c3790add361157dfa42854c3159c956f72e6acd8fabc518615f1ce8525'
def b(k,a):return prg[k*16384+(a&16383)]
def w(k,a):return b(k,a)+256*b(k,a+1)
def pose(i):
 at=w(2,0x8001+i*2);n=b(2,at);assert n<32;ptr=at+1;attr=0;parts=[]
 for _ in range(n):
  y,t=b(2,ptr),b(2,ptr+1);ptr+=2
  if not y&1:attr=b(2,ptr);ptr+=1
  x=b(2,ptr);ptr+=1;page=21 if t&1 else 0;pix=chr[page*4096+(t&254)*16:page*4096+(t&254)*16+32]
  parts.append({'dx':x if x<128 else x-256,'dy':(y if y<128 else y-256)//2,'tile':t,'attribute':attr,'physical_chr4k':page,'pixels':pix.hex()})
 return {'pose':i,'descriptor_address':at,'parts':parts}
ids=[60,61,62,63,72,73,74,75,76,80,81,82,83];poses=[pose(i)for i in ids];tiles=[];records={}
def encode(values):
 out=bytearray(32)
 for y in range(16):
  for x in range(8):
   for plane in range(2):out[y//8*16+y%8+plane*8]|=((values[y][x]>>plane)&1)<<(7-x)
 return bytes(out)
for q in poses:
 rec=[]
 for p in q['parts']:
  raw=bytes.fromhex(p['pixels']);values=[]
  for y in range(16):values.append([((raw[y//8*16+y%8]>>(7-x))&1)|(((raw[y//8*16+y%8+8]>>(7-x))&1)<<1)for x in range(8)])
  # Shared world P2 invariant red16/white30; P3 native dark ink. No enemy palette write.
  for pal,mapping in [(3,{1:1}),(2,{2:1,3:2})]:
   layer=[[mapping.get(c,0)for c in row]for row in values]
   if not any(any(row)for row in layer):continue
   data=encode(layer)
   if data not in tiles:tiles.append(data)
   rec.append([tiles.index(data)*2+1,(p['attribute']&0xc0)|pal,p['dy']&255,p['dx']&255])
 records[q['pose']]=rec
assert len(tiles)<=32,len(tiles)
lines=['; Authenticated TMNT1 original equipment pixels; explicit shared-world hue adaptation.','.pushseg','.segment "TMNT_GFX"','TnWorldArtStart:']
for face in ['R','L']:
 for suffix,op in [('Lo','<'),('Hi','>')]:
  lines.append('TnWorld'+face+suffix+':')
  for at in range(0,84,12):lines.append(' .byte '+','.join(op+('TnWorld'+str(i)+face if i in records else'TnWorldEmpty')for i in range(at,min(at+12,84))))
 for i,parts in records.items():
  lines.append('TnWorld'+str(i)+face+': .byte '+str(len(parts)*4))
  for t,a,y,x in reversed(parts):
   if face=='L':x=(-((x+128)%256-128)-8)&255;a^=0x40
   lines.append(' .byte '+','.join(map(str,[t,a,y,x])))
lines+=['TnWorldEmpty:.byte 0','.popseg','']
(D/'tmnt_secondary_art.inc').write_text('\n'.join(lines))
old=args.source_chr.read_bytes()[:24576];assert len(old)==24576 and hashlib.sha256(old).hexdigest()=='235ef1ba0d5c5a60205575b6d3fa8cf8bc9f31a6ea92dc2f3b2b0cadee4813d9'
new=old+b''.join(tiles)+bytes(1024-len(tiles)*32);(D/'tmnt.chr').write_bytes(new)
report={'original_ROM_sha256':hashlib.sha256(rom).hexdigest(),'old_body_primary_sha256':hashlib.sha256(old).hexdigest(),'old_prefix_bytes_unchanged':len(old),'new_asset_sha256':hashlib.sha256(new).hexdigest(),'world_page':628,'world_page_bytes':1024,'unique_tilepairs':len(tiles),'max_OAM_parts_per_pose':max(map(len,records.values())),'source_poses':poses,'records':records,'palette_adaptation':'Source equipment02/16/31 -> native darkP3.1 / invariant16P2.1 / white30P2.2. Original source pixels, coordinates and flips retained. Shared enemy palettes never rewritten.','addressing':'Odd8x16 indices select pattern table1/window4 physical628.'}
(D/'equipment-art-proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['source_poses','records']},indent=2))
