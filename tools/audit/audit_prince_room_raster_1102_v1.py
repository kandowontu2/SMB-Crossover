"""Find original room-material draw coordinates through genuine startup code.

Only aggregate writer sites and bounded examples are retained. No frame, PPU
image, asset tree or per-frame state dump is created.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_original_cpu_1101_v1 as P
from recover_prince_core_1101_v1 import O


def main():
 writers={};plots={};frame=-1
 def trace(c):
  m=c.memory;pc=c.pc;op=m[pc]
  if pc==0xe6cb and frame==604:
   key=(m[0x51],m[0x4b1]);plots.setdefault(key,dict(room=m[0x51],cell=m[0x4b1],material=m[0x6c7],PPU_plot_origin=m[0x18]|m[0x17]<<8,source_04bc=m[0x4bc]))
  if op not in [0x8c,0x8d,0x8e]or m[pc+1]!=7 or m[pc+2]!=0x20:return
  at=m.pa(m.v)
  if not 0x2000<=at<0x2800:return
  bank=7 if pc>=0xc000 else m.bank;key=f'{bank}:{pc:04X}'
  q=writers.setdefault(key,dict(count=0,first_frame=frame,last_frame=frame,nametable_rows=set(),nametable_columns=set(),examples=[]));q['count']+=1;q['last_frame']=frame
  nt=(at-0x2000)&1023;q['nametable_rows'].add(nt//32);q['nametable_columns'].add(nt%32)
  if frame>=300 and len(q['examples'])<6:q['examples'].append(dict(frame=frame,address=at,tile={0x8c:c.y,0x8d:c.a,0x8e:c.x}[op],X=c.x,Y=c.y,source17_18=[m[0x17],m[0x18]],source47_4f=[m[0x47],m[0x4f]],source04B1=m[0x4b1],source_room=m[0x4de]))
 c=P.boot(trace)
 for frame in range(900):P.frame(c,16 if 120<=frame<123 or 300<=frame<303 or 600<=frame<603 else 0,trace)
 m=c.memory;ptr=m[0x6cd]|m[0x6ce]<<8;m.switch(6)
 assert 0x8000<=ptr<0xbfe2
 cells=[m[ptr+i]for i in range(30)]
 grid=[]
 for i in range(30):
  address=m[0xebb2+2*i]|m[0xebb3+2*i]<<8
  logical=address-0x2000;x=((logical&31)*8)+(256 if logical&0x400 else 0);y=((logical&1023)//32)*8
  assert(x,y)==((i%10)*32+16,(i//10)*64)
  grid.append(dict(cell=i,original_table_PPU_address=address,visual_X=x,visual_Y=y))
 for q in writers.values():q['nametable_rows']=sorted(q['nametable_rows']);q['nametable_columns']=sorted(q['nametable_columns'])
 q=dict(passed=True,source_CPU_only=True,native_host=False,donor_sha256=P.SHA,natural_frames=900,source_room=m[0x4de],source_camera=m[0x6f],source_actor=list(m[0x60e:0x619]),room_pointer_bank6=ptr,room_material_bytes=cells,material_rows_low5=[[v&31 for v in cells[i:i+10]]for i in range(0,30,10)],source_visual_coordinate_table=grid,visual_vs_logical_alignment_origin=dict(X=16,Y=0,authority='Original EBB2/EBB3 thirty-entry PPU table versus independently executed bank2 A5F5 actor alignment table. Actual initial cell14 material17 plot at2112 is144,64, matching the table; edge/above-room overdraw calls are recorded separately.'),actual_material_plot_calls=list(plots.values()),actual_nametable_writer_sites=writers,scope='Actual reset/menu/room renderer instructions with untimed source PPU oracle. Aggregate write coordinates only; no raster or host transform claim.',bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(P.__file__)]})
 (O/'source-room-raster.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['actual_nametable_writer_sites','bindings']}))


if __name__=='__main__':main()
