"""Propose bounded shoe-only masks from original native pixels, no CHR lease."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import P,O,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from PIL import Image,ImageDraw
sha=lambda b:hashlib.sha256(b).hexdigest()

def reverse(v):return int(format(v,'08b')[::-1],2)

def main():
 b=scoped_load(P/'candidate.nes');r=b['raw'];assert sha(r)==PIN
 physical=r[location(b,'ChrPhysicalMap'):location(b,'ChrPhysicalMap')+256]
 bank=location(b,'PlayerBankTableReal')-address(b,'METASPRITE_BIG_MARIO_STANDING')
 atlas=[];records=[];counts={};palette=[(23,28,39),(245,245,238),(238,145,58),(113,62,32)]
 canvas=Image.new('RGB',(14*64,4*96),palette[0]);draw=ImageDraw.Draw(canvas)
 for face,prefix in [('R','MetaspriteTableRight'),('L','MetaspriteTableLeft')]:
  lo,hi=[location(b,prefix+x)for x in['Lo','Hi']];base=lo-address(b,prefix+'Lo')
  for pose in range(1,29):
   page=r[bank+pose];data=r[1048592+physical[page]*1024:1048592+(physical[page]+1)*1024]
   ptr=r[lo+pose]+256*r[hi+pose];at=base+ptr;n=r[at]
   pixels={};parts=[]
   for j in range(1,n+1,4):
    tile,attr,y,x=r[at+j:at+j+4];tile&=62;x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
    for yy in range(16):
     d=data[(tile+yy//8)*16:(tile+yy//8+1)*16];row=yy&7
     for xx in range(8):
      color=((d[row]>>(7-xx))&1)|(((d[row+8]>>(7-xx))&1)<<1)
      dx=x+(7-xx if attr&64 else xx);dy=y+(15-yy if attr&128 else yy)
      if color:pixels[dx,dy]=color
   # Explicit adaptation: each original8px leg column contributes the lowest
   # three rows of its original brown pixels. Shoes are never synthesized or
   # inferred from transparent cells, and the entire lower body is not flashed.
   # Human review is required before admitting this semantic shoe selection.
   selected=set()
   for left in [0,8]:
    candidates=[(x,y)for (x,y),color in pixels.items()if color==3 and left<=x<left+8 and y>=16]
    if not candidates:continue
    bottom=max(y for x,y in candidates);shoe={(x,y)for x,y in candidates if y>=bottom-2};selected|=shoe
    minx=min(x for x,y in shoe);miny=min(y for x,y in shoe);width=max(x for x,y in shoe)-minx+1;height=max(y for x,y in shoe)-miny+1
    rows=[0]*16
    for x,y in shoe:rows[y-miny]|=1<<(7-(x-minx))
    def encode(hflip,vflip):
     chosen=[rows[height-1-y if vflip else y]if y<height else 0 for y in range(16)]
     if hflip:chosen=[reverse(v)<<(8-width)for v in chosen]
     return bytes(chosen[:8])+bytes(8)+bytes(chosen[8:])+bytes(8)
    # Canonicalize the reflection within its occupied bounds. Full-tile
    # reflection without normalization would defeat matching mirrored poses.
    canonical,hflip,vflip=min((encode(h,v),h,v)for h in [False,True]for v in [False,True])
    if canonical not in atlas:atlas.append(canonical)
    # Hardware Hflip reflects the entire8px tile, so compensate its empty
    # left margin in the OAM origin rather than moving any source pixel.
    drawx=minx-(8-width if hflip else 0);drawy=miny-(16-height if vflip else 0)
    decoded=set()
    for yy in range(16):
     tile=canonical[(yy//8)*16:(yy//8+1)*16];row=yy&7
     for xx in range(8):
      color=((tile[row]>>(7-xx))&1)|(((tile[row+8]>>(7-xx))&1)<<1)
      if color:decoded.add((drawx+(7-xx if hflip else xx),drawy+(15-yy if vflip else yy)))
    assert decoded==shoe,(face,pose,drawx,minx,width)
    parts.append(dict(mask=atlas.index(canonical),x=drawx,y=drawy,hardware_flip=(64 if hflip else 0)|(128 if vflip else 0),source_pixels=sorted(shoe),pixel_reconstruction_passed=True))
   assert selected and selected<=set(k for k,v in pixels.items()if v==3)
   records.append(dict(face=face,pose=pose,parts=parts));counts[len(parts)]=counts.get(len(parts),0)+1
   image=Image.new('RGB',(24,40),palette[0]);pix=image.load()
   for (x,y),color in pixels.items():
    if 0<=x<24 and 0<=y<40:pix[x,y]=(255,55,95)if(x,y)in selected else palette[color]
   index=pose-1+(28 if face=='L'else 0);x=index%14*64;y=index//14*96
   canvas.paste(image.resize((48,80),Image.Resampling.NEAREST),(x+8,y));draw.text((x+8,y+82),face+str(pose),fill=(245,245,245))
 payload=b''.join(atlas);(O/'shoe-mask-candidate.chr').write_bytes(payload);canvas.save(O/'shoe-mask-review.png')
 q=dict(passed=True,semantic_visual_admission=False,CHR_lease_granted=False,source_ROM_sha256=PIN,poses=len(records),right_left=True,unique_masks=len(atlas),mask_bytes=len(payload),authentic_pickup_bytes=64,total_mask_plus_pickup_bytes=len(payload)+64,maximum_extra_OAM_sprites=max(counts),hardware_Hflip_deduplicated=True,hardware_Vflip_deduplicated=True,records=records,payload_sha256=sha(payload),
  adaptation='Lowest three brown rows per original8px leg column, from exact source pixels; normalized for OAM origin and canonical H/Vflip. Every output sprite is decoded and reconstructed against the exact selected source pixels. Review image highlights proposed shoe pixels pink. This is a proposed shoe mask, not a claim the donor contains worn-boots flashing.',
  render_contract=['Draw masks before native body OAM so mask pixels win sprite priority; do not append opaque masks behind earlier body sprites.','Existing SpecialDrawShots prepass is a candidate source hook; count the two emitted sprites before the unchanged16B native Mario body reservation.','Masks may use existing palette indices0..3 on source2-frame cadence; no global enemy/player palette rewrites are implied.','Need actual source-granted tile intervals, chosen sprite windows and normal/lag NMI paired publication proof before rendering.'],sources={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'shoe-mask-candidate.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['records','sources','render_contract','adaptation']}))

if __name__=='__main__':main()
