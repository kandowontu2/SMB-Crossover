"""Read-only FF lives scroll/NMI and native opaque-pixel diagnostic.

No ROM mutation, native run, video normalization or hardware timing claim.
"""
from pathlib import Path
import csv, hashlib, json, sys
from PIL import Image
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
import ff_cold_preview_controls_v1 as UI
from check_tmnt_render_oa import address
H=C.H
J=R/'build/arthur-goku-smb2-palette-v1/joint'
O=R/'build/ff-lives-scroll-diagnostic-v1'
N=R/'build/final62-ff-bg-eye-native-1030-v1/native/white-mage-cold-v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sprite_pixels(raw,page,parts):
 out={}
 # NES low physical OAM index wins; reverse iteration mirrors that rule.
 for sy,t,a,sx in reversed(parts):
  for yy in range(16):
   py=15-yy if a&128 else yy
   at=1048592+page*1024+((t&254)+py//8)*16+py%8
   for xx in range(8):
    bit=xx if a&64 else 7-xx
    v=(raw[at]>>bit&1)|((raw[at+8]>>bit&1)<<1)
    if v:out[sx+xx,sy+1+yy]=v
 return out
def opaque_native(m):
 raw=m.bundle['raw'];lives=Image.open(N/'lives.png').convert('RGB')
 body=UI.exact_body(m);pix=sprite_pixels(raw,body['physical_page'],body['OAM'])
 colors={v:set()for v in [1,2,3]}
 for xy,v in pix.items():colors[v].add(lives.getpixel(xy))
 assert all(len(c)==1 for c in colors.values()),colors
 colors={v:next(iter(c))for v,c in colors.items()}
 jump=Image.open(N/'source-jump.png').convert('RGB')
 rows=list(csv.DictReader((N/'gameplay-OAM.csv').open()))
 matches=[]
 for row in rows:
  if not 328<=int(row['frame'])<=342:continue
  data=bytes.fromhex(row['records64hex']);parts=[data[i:i+4]for i in range(0,256,4)if data[i]<240 and data[i+1]<64 and data[i+2]&3==0]
  page=int(row['page']);points=sprite_pixels(raw,page,parts)
  for dx in range(-6,7):
   for dy in range(-12,13):
    count=sum(jump.getpixel((x+dx,y+dy))==colors[v]for(x,y),v in points.items()if 0<=x+dx<256 and 0<=y+dy<240)
    matches.append(dict(frame=int(row['frame']),physical_page=page,dx=dx,dy=dy,matched=count,opaque=len(points),OAM=[list(p)for p in parts]))
 best=max(matches,key=lambda q:q['matched']/q['opaque'])
 return dict(lives_original_role_RGB=colors,lives_original_opaque=len(pix),jump_best_logged_source_OAM=best,
  scope='Exact PNG pixels against authenticated source CHR. Logged OAM is sparse, so any nonzero translation is disclosed, not a frame-state claim.',
  hashes={str(p):sha(p)for p in[N/'lives.png',N/'source-jump.png',N/'gameplay-OAM.csv',N/'normal-DMA-palette.csv']})
def nmi_trace(m):
 H.put(m,NmiDisable=0)
 c=H.start(m,'FwCheck');before=C.A.V.cpu_state(c);start=c.processorCycles
 c.nmi();rows=[];dma=0;counts={};low=c.sp
 for step in range(100000):
  if C.A.V.cpu_state(c)==before:break
  pc=c.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
  mark=len(m.writes);cycle=c.processorCycles-start
  c.step();low=min(low,c.sp)
  for a,v in m.writes[mark:]:
   if a in [0x2000,0x2001,0x2005,0x2006,0x4014]:
    rows.append(dict(cycle=cycle,pc=pc,raw_bank=tag,address=a,value=v,ScreenRoutineTask=H.get(m,'ScreenRoutineTask')))
   if a==0x4014:dma+=513 # Explicit nominal DMA addend; no DMC steals modeled.
 else:raise AssertionError('NMI did not return')
 H.finish(m,c)
 return dict(CPU_excluding_DMA=c.processorCycles-start,nominal_DMA_addend=dma,minimum_SP=low,events=rows,
  scope='Real assembled NMI instruction cycle/order. DMA addend is nominal only; no native PPU phase or DMC timing claim.')
def main():
 O.mkdir(exist_ok=True);out=O/'diagnostic.json';assert not out.exists()
 H.O=J;b=H.C.qualified(J/'candidate.nes');lives=[];original=C.A.consume;image=[]
 def consume(m):
  if H.get(m,'ScreenRoutineTask')==7 and sum(r['variant']==H.get(m,'FfVariant')for r in lives)<2:
   lives.append(dict(variant=H.get(m,'FfVariant'),queue_offset=H.get(m,'VRAM_Buffer1_Offset'),
    queue=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+64]),
    HorizontalScroll=H.get(m,'HorizontalScroll'),VerticalScroll=H.get(m,'VerticalScroll'),
    DisableScreenFlag=H.get(m,'DisableScreenFlag'),trace=nmi_trace(m)))
   if not image and H.get(m,'FfVariant')==1:image.append(opaque_native(m))
   return dict(diagnostic_real_NMI=True)
  return original(m)
 C.A.consume=consume
 try:sequence=C.four_classes(b)
 finally:C.A.consume=original
 # Image sampling can use a separate authentic lives frame if the first
 # twelve queue samples were all Fighter; no source state is overwritten.
 if not image:
  def sample(m):
   if not image and H.get(m,'ScreenRoutineTask')==7 and H.get(m,'FfVariant')==1:image.append(opaque_native(m))
   return original(m)
  C.A.consume=sample
  try:C.four_classes(b)
  finally:C.A.consume=original
 q=dict(source_read_only=True,native=False,candidate=sha(J/'candidate.nes'),lives=lives,opaque=image,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',Path(C.__file__),Path(UI.__file__)]})
 out.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(path=str(out),lives_samples=len(lives),opaque=image)),flush=True)
if __name__=='__main__':main()
