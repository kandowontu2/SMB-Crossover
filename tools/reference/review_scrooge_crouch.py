"""Record an independent native DuckTales crouch silhouette from hardware OAM."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'build/scrooge-reference/current/scrooge-1300'
oam=BASE.with_suffix('.oam').read_bytes()
chrdata=BASE.with_suffix('.chr').read_bytes()
parts=[oam[i:i+4] for i in range(0,256,4)
       if 60<oam[i]<205 and oam[i+1]<128 and oam[i+2]&3 in (0,1,2)]
pixels=set()
for y,t,a,x in parts:
    for dy in range(8):
        yy=7-dy if a&128 else dy
        for dx in range(8):
            bit=dx if a&64 else 7-dx
            color=((chrdata[t*16+yy]>>bit)&1)|(((chrdata[t*16+yy+8]>>bit)&1)<<1)
            if color:
                pixels.add((x+dx,y+1+dy))
x0=min(x for x,y in pixels);x1=max(x for x,y in pixels)
y0=min(y for x,y in pixels);y1=max(y for x,y in pixels)
rows=[''.join('1' if (x,y) in pixels else '0' for x in range(x0,x1+1)) for y in range(y0,y1+1)]
body=next(p for p in parts if p[2]&3==0)
if not body[2]&64:
    rows=[row[::-1] for row in rows]
assert y1-y0+1<32, 'Native crouch must be visibly shorter than standing'
target=ROOT/'tests/scrooge-native-crouch.lua'
target.write_text('-- Independent native DuckTales frame1300, Down+Right held; normalized right.\nreturn {\n'+''.join(' "'+row+'",\n' for row in rows)+'}\n')
metadata=json.loads((ROOT/'docs/reference/scrooge.json').read_text())
metadata['crouch_capture']={
    'script':'tools/reference/scrooge-movement-probe.lua', 'frame':1300,
    'controls':'Down+Right held on stationary ground, no emulated writes',
    'opaque_bounds_native':[x0,y0,x1,y1],
    'source_sha256':metadata['source_sha256'],
    'captures_sha256':{ext:hashlib.sha256(BASE.with_suffix(ext).read_bytes()).hexdigest() for ext in ('.chr','.oam','.pal','.png')},
    'reference_lua_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
}
(ROOT/'docs/reference/scrooge.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(f'PASS independent native crouch: {x1-x0+1}x{y1-y0+1}, {len(parts)} OAM parts')
