"""Bound native Mario art and identify candidates without allocating CHR."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_host_1101_v2 import P,O,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from PIL import Image,ImageDraw
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 b=scoped_load(P/'candidate.nes');r=b['raw'];assert sha(r)==PIN
 at=location(b,'ChrPhysicalMap');physical=r[at:at+256]
 pages={n:r[1048592+physical[n]*1024:1048592+(physical[n]+1)*1024]for n in range(16,21)}
 native=b''.join(pages[n]for n in range(16,20));donor=(R/'build/mario-tank-source-1101-v1/mario-body.chr').read_bytes();assert native==donor
 data_base=location(b,'MetaspriteTableRightLo')-address(b,'MetaspriteTableRightLo')
 lo,hi=[location(b,'MetaspriteTableRight'+q)for q in['Lo','Hi']]
 bank=location(b,'PlayerBankTableReal')-address(b,'METASPRITE_BIG_MARIO_STANDING')
 records=[];used={n:set()for n in range(16,20)};canvas=Image.new('RGB',(16*48,4*64),(25,30,42));draw=ImageDraw.Draw(canvas)
 colors=[(25,30,42),(248,248,248),(245,157,72),(105,59,28)]
 for index in range(1,63):
  p=r[lo+index]+256*r[hi+index];at=data_base+p;size=r[at];assert size%4==0 and size<=32
  logical=r[bank+index];assert logical in pages
  parts=[];frame=Image.new('RGB',(16,40),colors[0]);pix=frame.load()
  for j in range(1,size+1,4):
   tile,attr,y,x=r[at+j:at+j+4];tile&=0xfe;x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
   local=tile&63;used[logical].update([local,local+1]);parts.append(dict(tile_pair=[local,local+1],x=x,y=y,attributes=attr))
   for yy in range(16):
    pattern=local+yy//8;row=yy&7;plane=pages[logical][pattern*16:pattern*16+16]
    for xx in range(8):
     shift=7-xx;color=((plane[row]>>shift)&1)|(((plane[row+8]>>shift)&1)<<1)
     dx=x+(7-xx if attr&64 else xx);dy=y+(15-yy if attr&128 else yy)+8
     if color and 0<=dx<16 and 0<=dy<40:pix[dx,dy]=colors[color]
  records.append(dict(index=index,logical_bank=logical,physical_bank=physical[logical],parts=parts))
  x=((index-1)%16)*48;y=((index-1)//16)*64;canvas.paste(frame.resize((32,40),Image.Resampling.NEAREST),(x+8,y+4));draw.text((x+5,y+47),str(index)+'/'+str(logical),fill=(245,245,245))
 canvas.save(O/'native-Mario-source-poses.png')
 candidate={}
 for n in range(16,20):
  free=sorted(set(range(64))-used[n]);blank=[i for i in free if not any(pages[n][i*16:(i+1)*16])]
  candidate[n]=dict(logical_bank=n,physical_bank=physical[n],unreferenced_by_native_Mario_records=free,blank_unreferenced=blank,bytes=16*len(blank),other_owner_closure=False)
 q=dict(passed=True,ROM_sha256=PIN,native_Mario_equals_authentic_Tank_body=True,Mario_body_CHR_growth_required=0,body_bytes=4096,body_sha256=sha(native),native_Mario_records=records,candidate_tile_padding=candidate,CHR_lease_granted=False,
  conclusions=['Physical pages12..15 already contain the exact4096B original Tank Mario body; reuse without a new body atlas.','Native Mario pose table alone leaves candidate unused patterns. Zero-fill and native-Mario-only reference absence do not close Maaa/other actor/scene ownership, so no tile allocation is granted.','All1024 physical CHRpages are spoken for through Karnov1023. A new1KB boots/overlay page cannot be presumed.','Original64B boots pickup must remain distinct from other characters Fire Flower. Worn-boot-only flash requires a pose/facing-aligned masked layer or a proven palette strategy; recoloring whole lower-body tiles does not qualify.'],
  graphics_path='PlayerGfxHandler variant>=3 -> KmGraphics/BmGraphics -> KmNativeGraphics for7; lives/menu BmPortrait fallback uses native Mario descriptor. Native body can be reused, but Tank menu/lives name and dedicated worn overlay need explicit dispatch.',
  sources={str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes())})
 (O/'art-resource-audit.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['native_Mario_records','sources','conclusions']}))

if __name__=='__main__':main()
