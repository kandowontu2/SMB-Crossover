"""Preserve original8x16 art in actual native8x16 mode; no PNG/ROM writes."""
import json
import recover_bubble_bobble_source_1101_v1 as B
import check_bubble_bobble_closure_1101_v1 as C
O=B.O


def raster(rows,pattern):
 out={}
 for y,t,a,x in rows:
  data=pattern(t)
  for dy in range(16):
   yy=15-dy if a&128 else dy;tile,row=divmod(yy,8)
   for dx in range(8):
    xx=7-dx if a&64 else dx;v=((data[tile*16+row]>>(7-xx))&1)|(((data[tile*16+row+8]>>(7-xx))&1)<<1)
    if v and 0<=x+dx<256 and 0<=y+1+dy<240:out.setdefault((x+dx,y+1+dy),(a&35,v))
 return out


def main():
 raw=B.ROM.read_bytes()[16+131072:]
 atlas=(O/'donor-chr-closure.bin').read_bytes();assert len(atlas)==800
 metadata=json.loads((O/'chr-closure.json').read_text());mapping={r['oam_tile']:i*2+1 for i,r in enumerate(metadata['tiles'])}
 def original(t):
  bank=2 if t&1 else 1;at=bank*4096+(t&254)*16;return raw[at:at+32]
 def native(t):
  assert t&1;at=(t&254)*16;return atlas[at:at+32]
 records=[];digest=__import__('hashlib').sha256();opaque=0
 def check(name,oam):
  nonlocal opaque
  rows=[oam[i:i+4]for i in range(0,len(oam),4)];nr=[[y,mapping[t],a,x]for y,t,a,x in rows]
  a=raster(rows,original);b=raster(nr,native);assert a==b,name;opaque+=len(a);digest.update(repr(sorted(b.items())).encode())
  # Native emitter descends; reversed records retain original OAM priority.
  ox,oy=rows[0][3],rows[0][0];packet=[4*len(rows)]
  for y,t,attr,x in reversed(nr):packet.extend([t,attr,(y-oy)&255,(x-ox)&255])
  records.append(dict(case=name,sprites=len(rows),native_packet=packet))
 poses=json.loads((O/'CPU-closure.json').read_text())['poses']
 for pose in poses:check('body:%d:%d:%d'%(pose['actor'],pose['pose'],pose['facing']),pose['OAM'])
 for phase in range(6):
  for palette in [0,3]:
   for flip in [0,64]:
    p=C.pair();C.put(p,0x88,[1,0,phase,8]);C.put(p,0x288,[100,0,palette|flip,100,100,0,palette|flip,108]);C.run(p,0xdf54,x=0x88,y=0x88,tag='native_art_source')
    check('bubble:%d:%d:%d'%(phase,palette,flip),list(p[0].memory[0x288:0x290]))
 (O/'component-native.chr').write_bytes(atlas+bytes(224))
 q=dict(passed=True,host_sprite_height=16,source_sprite_height=16,opaque_pixels=opaque,source_body_cases=len(poses),source_bubble_cases=48,native8x16_pairs=25,pattern_bytes=800,physical_page_bytes=1024,proposed_physical_page=441,granted=False,host_ROM_written=False,body_sprite_count=2,bubble_sprite_count=2,fifteen_bubbles_plus_body_sprites=32,source_native_raster_sha256=digest.hexdigest(),CHR_sha256=B.sha((O/'component-native.chr').read_bytes()),source_to_native_tile={str(k):v for k,v in mapping.items()},packets=records,scope='Actual host8x16 convention confirmed by current Shinobi/Excitebike native packers. Every normal body/bubble source pixel/palette/priority/flip equals remapped paired tiles. No hardware OAM/scanline/PPU publication/native performance proof. Corrects earlier8x8-host OAM estimate.')
 (O/'native-art.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','source_body_cases','source_bubble_cases','native8x16_pairs','body_sprite_count','bubble_sprite_count','host_ROM_written']}))


if __name__=='__main__':main()
