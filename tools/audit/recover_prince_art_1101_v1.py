"""Generate Prince pose packets via original renderer and CHR-RAM upload code."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as P
O=R/'build/prince-actor-1101-v1'


def pattern(raw,attr):
 rows=[]
 for y in range(8):
  sy=7-y if attr&128 else y
  values=[]
  for x in range(8):
   sx=x if attr&64 else 7-x
   values.append(((raw[sy]>>sx)&1)|(((raw[sy+8]>>sx)&1)<<1))
  rows.append(values)
 return rows


def encode(rows):
 low=[];high=[]
 for row in rows:
  low.append(sum((v&1)<<(7-x)for x,v in enumerate(row)))
  high.append(sum(((v>>1)&1)<<(7-x)for x,v in enumerate(row)))
 return bytes(low+high)


def main():
 q=json.loads((O/'core-CPU.json').read_text());frames=sorted({v for s in q['sequences']for v in s['frames']if v})
 seed=(O/'state-899.bin').read_bytes();raw=P.donor();poses=[];atlas=[];unique={};nativepatterns=set();totalcells=0;maxcells=0;historical_matches=[]
 historical='2e057652662d52a346cb6f2f5ca3414d22557d20b465baf5f6e834f7109fcb13'
 for frame in frames:
  for face in [0,255]:
   c=P.machine();list.__setitem__(c.memory,slice(0,2048),seed)
   for p,v in {0x60f:128,0x610:0,0x611:112,0x612:0,0x615:face,0x617:frame,0x69:0,0x77:0,0x2a:0,0x29:0,0x35:0xcc,0x6f:0,0x6e0:0,0x401:0,0x4cc:0}.items():c.memory[p]=v
   list.__setitem__(c.memory,slice(0x200,0x300),bytes(256))
   c.memory.switch(4);P.call(c,0xb449,x=0,limit=100000)
   geometry=dict(native_070F=c.memory[0x70f],native_06F1_minus_anchor_y=(c.memory[0x6f1]-112)&255,native_04C3=c.memory[0x4c3])
   cursor=c.memory[0x35];assert cursor%4==0 and cursor<=252,(frame,face,cursor)
   cells=[]
   for at in range(0,256,4):
    y,tile,attr,x=c.memory[0x200+at:0x204+at]
    if tile==0:continue # Native renderer explicitly rejects source tile0.
    cells.append(dict(x=x-128,y=y+1-112,tile=tile,attribute=attr))
   # Execute the genuine upload path with its documented alternate PPU-write
   # mode (53=1); no copied ROM tile ordinal is treated as an art asset.
   for p,v in {0x53:1,0x27:0,0x28:16,0x65:0}.items():c.memory[p]=v
   c.memory.switch(5);P.call(c,0xf325,x=0,limit=100000)
   for cell in cells:
    t=cell['tile'];p=bytes(c.memory.ppu[t*16:t*16+16]);nativepatterns.add(p);cell['raw']=p;cell['pixels']=pattern(p,cell['attribute'])
   if sorted({v['tile']for v in cells})==list(range(1,10)):
    packed=b''.join(bytes(c.memory.ppu[t*16:t*16+16])for t in range(1,10))
    if hashlib.sha256(packed).hexdigest()==historical:historical_matches.append([frame,face])
   # Pair exact same-X cells one tile apart with identical source attributes.
   # Retain native horizontal flip and reverse halves for whole-pair Y flip.
   used=set();parts=[]
   for i in sorted(range(len(cells)),key=lambda i:(cells[i]['y'],cells[i]['x'],i)):
    cell=cells[i]
    if i in used:continue
    attr=cell['attribute']&0xe3;mate=None
    for j,other in enumerate(cells):
     if j not in used and j!=i and other['x']==cell['x']and other['y']==cell['y']+8 and other['attribute']&0xe3==attr:mate=j;break
    top=cell['raw'];bottom=cells[mate]['raw']if mate is not None else bytes(16)
    pair=(bottom+top)if attr&128 else(top+bottom);number=unique.get(pair)
    if number is None:number=len(atlas);unique[pair]=number;atlas.append(pair)
    parts.append(dict(x=cell['x'],y=cell['y'],pattern_pair=number,attribute=attr,source_cells=[i]+([mate]if mate is not None else[])))
    used.add(i)
    if mate is not None:used.add(mate)
   parts.sort(key=lambda p:min(p['source_cells']))
   def raster_source():
    pixels={}
    for cell in reversed(cells):
     for y,row in enumerate(cell['pixels']):
      for x,v in enumerate(row):
       if v:pixels[cell['x']+x,cell['y']+y]=(cell['attribute']&0x23,v)
    return pixels
   def raster_pair():
    pixels={}
    for part in reversed(parts):
     pair=atlas[part['pattern_pair']];rows=pattern(pair[:16],part['attribute']&64)+pattern(pair[16:],part['attribute']&64)
     if part['attribute']&128:rows.reverse()
     for y,row in enumerate(rows):
      for x,v in enumerate(row):
       if v:pixels[part['x']+x,part['y']+y]=(part['attribute']&0x23,v)
    return pixels
   assert raster_source()==raster_pair(),('Packet projection mismatch',frame,face)
   for cell in cells:cell.pop('pixels');cell.pop('raw')
   totalcells+=len(cells);maxcells=max(maxcells,len(parts));poses.append(dict(source_frame=frame,source_facing=face,source_pattern_group=c.memory[0x600],source_projection_geometry=geometry,source_cells=cells,parts_8x16=parts))
 (O/'prince-body-8x16.chr').write_bytes(b''.join(atlas))
 assert historical_matches,'New original renderer/uploader must reproduce an authenticated historical body pattern packet'
 result=dict(passed=True,source_CPU_only=True,native=False,donor_sha256=P.SHA,source_frames=len(frames),source_facing_packets=len(poses),original_B449_and_F325_executed=True,source_cells=totalcells,source_unique_8x8_patterns=len(nativepatterns),native_8x16_pattern_pairs=len(atlas),pattern_bytes=len(atlas)*32,CHR_1KB_pages=(len(atlas)*32+1023)//1024,maximum_8x16_sprites_per_pose=maxcells,all_source_palette_index_pixels_exact=True,historical_body_pattern_sha256=historical,historical_body_matching_frame_facing=historical_matches,poses=poses,limits=['Packets generated by actual original renderer and genuine alternate-mode CHRRAM uploader in CPU oracle; not fresh Mesen captures.','Frames come from all93action scripts through their first pointer cycle, including hidden frame0 continuations; opcode9 is separately direct-tested.','All93actiontable rows include source enemy/scene programs; host player action eligibility must be constrained by original controller/state.','The paired atlas is a resource request only; no CHR pages allocated or published.','Sprite-limit/OAMcapacity/PPUdeadline and host palette ownership remain unqualified.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__),O/'core-CPU.json',O/'state-899.bin',O/'prince-body-8x16.chr']})
 (O/'source-art.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['poses','bindings']}))


if __name__=='__main__':main()
