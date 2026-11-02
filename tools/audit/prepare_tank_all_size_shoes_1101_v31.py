"""Exact shoe-only masks for normal Mario in both sizes and both facings."""
from pathlib import Path
import hashlib,json
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2];O=R/'build/tank-all-size-shoes-1101-v31'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(R/'build/mario-tank-visible-host-1101-v5/candidate.nes');r=b['raw']
 physical=r[location(b,'ChrPhysicalMap'):location(b,'ChrPhysicalMap')+256];bank=location(b,'PlayerBankTableReal')-1
 patterns=[];records=[];packed=[];lookup=[]
 for face in ['Right','Left']:
  lo,hi=[location(b,'MetaspriteTable'+face+x) for x in ['Lo','Hi']];base=lo-address(b,'MetaspriteTable'+face+'Lo')
  for pose in range(1,63):
   page=physical[r[bank+pose]];data=r[1048592+page*1024:1048592+(page+1)*1024]
   at=base+r[lo+pose]+256*r[hi+pose];pixels={}
   for j in range(1,r[at]+1,4):
    tile,a,y,x=r[at+j:at+j+4];tile&=62;x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
    for yy in range(16):
     raw=data[(tile+yy//8)*16:(tile+yy//8+1)*16];row=yy%8
     for xx in range(8):
      v=((raw[row]>>(7-xx))&1)|(((raw[row+8]>>(7-xx))&1)<<1)
      if v:pixels[x+(7-xx if a&64 else xx),y+(15-yy if a&128 else yy)]=v
   parts=[]
   for left in [0,8]:
    # Fire-small and growth poses use four cells, unlike ordinary small Mario.
    p=[(x,y) for (x,y),v in pixels.items() if v==3 and left<=x<left+8 and y>=(16 if r[at]==16 else 0)]
    if not p:continue
    bottom=max(y for x,y in p);shoe=set((x,y) for x,y in p if y>=bottom-2)
    minx=min(x for x,y in shoe);miny=min(y for x,y in shoe);w=max(x for x,y in shoe)-minx+1;h=max(y for x,y in shoe)-miny+1
    options=[]
    for flip in [0,64,128,192]:
     rows=[0]*16
     for x,y in shoe:
      px=x-minx;py=y-miny
      if flip&64:px=w-1-px
      if flip&128:py=h-1-py
      rows[py]|=1<<(7-px)
     options.append((bytes(rows[:8])+bytes(8)+bytes(rows[8:])+bytes(8),flip))
    pattern,flip=min(options)
    if pattern not in patterns:patterns.append(pattern)
    dx=minx-(8-w if flip&64 else 0);dy=miny-(16-h if flip&128 else 0)
    decoded=set()
    for y in range(16):
     for x in range(8):
      if pattern[(y//8)*16+y%8]&(1<<(7-x)):decoded.add((dx+(7-x if flip&64 else x),dy+(15-y if flip&128 else y)))
    assert decoded==shoe
    parts.append(dict(mask=patterns.index(pattern),x=dx,y=dy,flip=flip,pixels=sorted(shoe)))
   assert parts,(face,pose)
   record=bytes(v for p in parts for v in [p['mask'],p['flip'],p['x']&255,p['y']&255])
   if record not in packed:packed.append(record)
   lookup.append(sum(map(len,packed[:packed.index(record)])))
   records.append(dict(face=face,pose=pose,parts=parts))
 assert len(patterns)<128
 blob=b''.join(patterns);(O/'shoes.chr').write_bytes(blob)
 # 16-bit offsets because all-size records can exceed the old byte index.
 (O/'records.bin').write_bytes(b''.join(packed))
 q=dict(passed=True,ROM_sha256=hashlib.sha256(r).hexdigest(),poses=len(records),patterns=len(patterns),pattern_bytes=len(blob),unique_records=len(packed),record_bytes=sum(map(len,packed)),max_offset=max(lookup),lookup=lookup,records=records,host_wired=False,scope='Lowest three brown rows in each native leg column; all 124 pose/facing masks reconstruct exactly, including fire-small and growth. Both small and big Mario. No invented walking body artwork. Native integration and visual review pending.')
 (O/'masks.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k not in ['lookup','records']}))
if __name__=='__main__':main()
