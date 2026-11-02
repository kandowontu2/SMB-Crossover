"""Original executable coordinate/query contract before any SMB host binding.

The original room has32x64 cells, not SMB's16x16 block grid. Keep that
distinction explicit; these cases do not invent native terrain responses.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
from recover_prince_core_1101_v1 import O


def main():
 seed=(O/'state-899.bin').read_bytes();c=P.machine();cases={};offsets=[0,4,8,20,24,28,31,34,40,44,64]
 def reset(bank,fields):
  list.__setitem__(c.memory,slice(0,2048),seed)
  for at,value in fields.items():c.memory[at]=value
  c.memory.switch(bank)
 for world in range(512):
  for offset in offsets:
   reset(7,{0x60f:world&255,0x610:world>>8});P.call(c,0xf870,x=offset)
   assert c.memory[0x17]|c.memory[0x18]<<8==world+offset
   cases['original_add_X']=cases.get('original_add_X',0)+1
   reset(7,{0x60f:world&255,0x610:world>>8});P.call(c,0xfa6c,x=offset)
   expected=(world-offset)&65535
   # Source deliberately zeroes only the low byte at the room-left boundary;
   # it retains the high-byte negative/borrow signal consumed by room lookup.
   if world<offset:expected=0xff00
   assert c.memory[0x17]|c.memory[0x18]<<8==expected,(world,offset,expected)
   cases['original_sub_X_with_room_boundary']=cases.get('original_sub_X_with_room_boundary',0)+1
 for world in range(512):
  reset(2,{0x17:world&255,0x18:world>>8});P.call(c,0xa8d6)
  expected=min(world>>5,9)
  assert c.memory[0x4b1]==c.memory[0x4b2]==expected
  cases['original_column32_clamp9']=cases.get('original_column32_clamp9',0)+1
 for y in range(256):
  for col in range(10):
   reset(2,{0x17:y,0x4b1:col,0x4b2:col});P.call(c,0xa86a)
   expected=col+10*(y>>6)
   if expected>=30:expected-=10
   assert c.memory[0x4b1]==c.memory[0x4b2]==expected
   cases['original_row64_three_rows']=cases.get('original_row64_three_rows',0)+1
 raw=P.donor();base=16+2*16384;table=raw[base+0x25f5:base+0x25f5+90]
 assert len(table)==90
 for cell in range(30):
  assert table[3*cell]|table[3*cell+1]<<8==(cell%10)*32
  assert table[3*cell+2]==(cell//10)*64
  for dx,dy in [(0,64),(0,0),(4,64),(40,29),(255,255)]:
   for face in [0,255]:
    for mode in [0,1]:
     reset(2,{0x4b1:cell,0x17:dx,0x18:dy,0x615:face,0x4fe:mode})
     P.call(c,0xae78)
     world=(cell%10)*32+dx
     # Literal source adaptation below changes only low X, without a carry
     # propagation. Keep this exact behavior; it is not a max/clamp formula.
     if mode and face==0:world=(world&0xff00)|((world-30)&255)
     assert c.memory[0x60f]|c.memory[0x610]<<8==world
     assert c.memory[0x611]==((cell//10)*64+dy)&255
     cases['original_align_table_all30cells']=cases.get('original_align_table_all30cells',0)+1
 roots={
  'add_X':(7,0xf870,18),'subtract_X':(7,0xfa6c,29),
  'column':(2,0xa8d6,24),'row':(2,0xa86a,48),'align':(2,0xae78,56),
  'world_pointer':(7,0xd4a2,19),'tile_type':(7,0xce63,8),
  'feet_X':(7,0xd120,12),'ahead_X':(7,0xf649,12)}
 byte_bindings={}
 for n,(bank,pc,size)in roots.items():
  at=16+bank*16384+(pc&(0x3fff));data=raw[at:at+size]
  byte_bindings[n]=dict(bank=bank,PC=hex(pc),bytes=size,hex=data.hex(),sha256=hashlib.sha256(data).hexdigest())
 q=dict(passed=True,source_CPU_only=True,native_host=False,resource_granted=False,donor_sha256=P.SHA,cases=cases,total_cases=sum(cases.values()),source_room_geometry=dict(columns=10,rows=3,cell_width=32,cell_height=64,source_cell_coordinate_table=table.hex()),source_query_offsets=dict(feet_subtract_X={'facing0':31,'facing_nonzero':20},ahead_subtract_X={'facing0':40,'facing_nonzero':4},row_subtract_Y={'ordinary':29,'actions3_4_14':36}),source_tile_read='Bank6 room pointer06CD/06CE -> temporary0C/0D, indexed by04B1; AND1F returns original tile type.',instructions=byte_bindings,host_binding_requirements=['SMB16x16 terrain cannot be assigned directly as original10x3 room bytes. Preserve original motion/scripts, then bind each environment query to actual native geometry with an explicit coordinate transform.','Original renderer uses source actor X minus source camera6F; body packets are already source-executed. Constructor/export/bbox anchors must be qualified together, never inferred from a Mario body rectangle.','Original low-byte room-left sentinel and face-dependent query offsets are intentional observed source behavior; do not replace them with guessed clamps.','Next: derive real world query samples and host-native reads/returns for all20 callbacks. Three scene/gate/room-above boundary kinds remain unexercised in earlier core fixtures.'],bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[Path(__file__),Path(P.__file__),O/'state-899.bin',O/'core-recovery.json']})
 (O/'world-contract.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['instructions','bindings']}))


if __name__=='__main__':main()
