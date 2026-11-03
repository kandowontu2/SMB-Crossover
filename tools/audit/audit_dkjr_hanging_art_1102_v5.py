"""Prove whether existing source fruit sprite art covers original hanging fruit."""
import hashlib,json
from pathlib import Path
import prepare_dkjr_native_world_1102_v3 as P
R=P.R;O=P.O;D=P.P.D
sha=lambda b:hashlib.sha256(bytes(b)).hexdigest()


def main():
 raw=D.donor();chrdata=raw[16400:];bg=chrdata[4096:];matches={}
 for base in[0xa4,0xa8,0xac]:
  matches[str(base)]=[[t for t in range(256)if bg[t*16:(t+1)*16]==chrdata[(base+i)*16:(base+i+1)*16]]for i in range(4)]
 c,_=D.active();initial=c.memory;ptr=initial[0x91]+256*initial[0x92];records=[list(initial[ptr+1+i:ptr+8+i])for i in range(0,initial[0x93],7)];rows=[]
 def pixel(tile,x,y,bank=0):
  pos=bank*4096+tile*16+y;bit=7-x;return(chrdata[pos]>>bit&1)|((chrdata[pos+8]>>bit&1)<<1)
 for fx,fy,base,*restore in records:
  m=D.Bus();m[:2048]=bytes(initial[:2048]);m[0x213]=(fx-20)&255;m[0x210]=fy
  d=D.T.NesMPU(memory=m,pc=0);D.T.run(d,0xd2bd);D.T.run(d,0xd955);assert m[0x8c]and m[0x231]==base
  cells=[list(m[0x230+i:0x234+i])for i in range(0,16,4)];assert len(cells)==4
  sprite=bytearray(256);sprite_rgb=bytearray(256);static=bytearray(256);static_rgb=bytearray(256);tiles=[];palettes=set()
  for y,t,attr,x in cells:
   for py in range(8):
    for px in range(8):
     dx=x-fx+px;dy=y-fy+py;assert 0<=dx<16 and 0<=dy<16
     v=pixel(t,px,py);sprite[dy*16+dx]=v;sprite_rgb[dy*16+dx]=initial.ppu[0x3f10+(attr&3)*4+v]if v else 0xff
  for py in range(16):
   for px in range(16):
    tx=(fx+px)//8;ty=(fy+py)//8;t=initial.ppu[0x2000+ty*32+tx];attribute=initial.ppu[0x23c0+(ty//4)*8+tx//4];shift=((ty&2)*2)+(tx&2);palette=attribute>>shift&3;palettes.add(palette)
    v=pixel(t,px&7,py&7,bank=1);static[py*16+px]=v;static_rgb[py*16+px]=initial.ppu[0x3f00+palette*4+v]if v else 0xff
  for yy in range(2):
   for xx in range(2):tiles.append(initial.ppu[0x2000+(fy//8+yy)*32+fx//8+xx])
  rows.append(dict(x=fx,y=fy,falling_base=base,static_BG_tiles=tiles,static_BG_palette_slots=sorted(palettes),falling_sprite_palette_slots=sorted({z[2]&3 for z in cells}),indices_exact=static==sprite,opaque_RGB_exact=static_rgb==sprite_rgb,static_indices_SHA256=sha(static),falling_indices_SHA256=sha(sprite),static_RGB_SHA256=sha(static_rgb),falling_RGB_SHA256=sha(sprite_rgb),source_hanging_BG_Y=fy,source_falling_OAM_Y=fy,original_handoff_visible_Y_shift=1,restore_tiles=restore))
 q=dict(passed=True,native=False,donor_SHA256=D.SHA,existing_atlas_bytes=1728,source_body_bytes=1408,source_falling_fruit_bytes=192,source_hit_bytes=128,source_fruit_tiles_BG_duplicates=matches,actual_original_stage1_hanging=rows,all_stage1_static_and_falling_opaque_RGB_equal=all(r['opaque_RGB_exact']for r in rows),all_three_fruit_sprite_pattern_groups_have_complete_BG_duplicates=all(all(v for v in rows)for rows in matches.values()),scope='Original reset/start PPU nametable/attribute/palette state and exact original fruit touch/renderer. No native art/palette mutation, additional CHR allocation or assumption that source sprite palettes fit alongside native enemies.',bindings={Path(__file__).relative_to(R).as_posix():P.P.sha(Path(__file__).read_bytes())})
 (O/'hanging-art-v5.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,all_stage1_static_and_falling_opaque_RGB_equal=q['all_stage1_static_and_falling_opaque_RGB_equal'],complete_BG_duplicates=q['all_three_fruit_sprite_pattern_groups_have_complete_BG_duplicates'],cases=rows)))


if __name__=='__main__':main()
