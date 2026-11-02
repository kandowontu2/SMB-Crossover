"""Lossless flip canonicalization and transparent-cell omission for death art."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];O=R/'build/metal-storm-death-art-1101-v28'

def pixels(raw):
 return bytes(((raw[(y//8)*16+y%8]>>(7-x))&1)|(((raw[(y//8)*16+y%8+8]>>(7-x))&1)<<1) for y in range(16) for x in range(8))

def flip(p,f):
 return bytes(p[(15-y if f&128 else y)*8+(7-x if f&64 else x)] for y in range(16) for x in range(8))

def encode(p):
 return bytes(sum(((p[y*8+x]>>bit)&1)<<(7-x) for x in range(8)) for half in range(2) for bit in range(2) for y in range(half*8,half*8+8))

def main():
 q=json.loads((O/'art.json').read_text());raw=(O/'explosion.chr').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==q['CHR_sha256']
 original=[pixels(raw[i:i+32]) for i in range(0,len(raw),32)]
 patterns=[];lookup={};packets=[];omitted=0
 def raster(cells,tiles):
  result={}
  # Earlier OAM cells win overlapping opaque pixels.
  for c in reversed(cells):
   p=flip(tiles[c['pattern']],c['attributes'])
   for y in range(16):
    for x in range(8):
     v=p[y*8+x]
     if v:result[c['dx']+x,c['dy']+y]=(c['attributes']&3,v,c['attributes']&32)
  return result
 for packet in q['packets']:
  cells=[]
  for c in packet['cells']:
   p=original[c['pattern']]
   if not any(p):omitted+=1;continue
   canon,f=min((flip(p,f),f) for f in [0,64,128,192])
   if canon not in lookup:lookup[canon]=len(patterns);patterns.append(canon)
   cells.append(dict(dx=c['dx'],dy=c['dy'],pattern=lookup[canon],attributes=c['attributes']^f))
  assert raster(packet['cells'],original)==raster(cells,patterns),packet['pose']
  packets.append(dict(pose=packet['pose'],cells=cells))
 blob=b''.join(encode(p) for p in patterns)
 assert all(pixels(blob[i*32:i*32+32])==p for i,p in enumerate(patterns))
 (O/'explosion-compact.chr').write_bytes(blob)
 result=dict(passed=True,source_art_sha256=hashlib.sha256((O/'art.json').read_bytes()).hexdigest(),patterns=len(patterns),CHR_bytes=len(blob),omitted_transparent_cells=omitted,original_cells=512,retained_cells=sum(len(p['cells']) for p in packets),maximum_cells=max(len(p['cells']) for p in packets),pixel_equivalent_poses=len(packets),packets=packets,host_allocated=False,scope='Exact pixel indices, palette attributes, priority and overlap order preserved. No recoloring or invented explosion frames. Native CHR allocation, callback integration and raster test still required.')
 (O/'compact.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='packets'}))
if __name__=='__main__':main()
