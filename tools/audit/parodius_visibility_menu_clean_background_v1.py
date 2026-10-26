"""Offline source-derived static menu pixel mask; no emulator or source mutation."""
from pathlib import Path
import argparse,collections,hashlib,json
from PIL import Image,ImageChops,ImageDraw
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def image(p):return Image.frombytes('RGBA',(256,240),Path(p).read_bytes(),'raw','BGRA').convert('RGB')
def mismatch(a,b,mask):
 d=ImageChops.difference(a,b);bands=d.split();m=ImageChops.lighter(ImageChops.lighter(bands[0],bands[1]),bands[2]).point(lambda v:255 if v else 0);m=ImageChops.multiply(m,mask)
 return m.histogram()[255],m.getbbox(),m

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 baseline=D/'parodius-menu3cee-preparation-v2/menu/baseline-early';bad=D/'parodius-menub0-preparation-v3/menu/baseline-early'
 z=json.loads((a.run/'lifecycle-proof.json').read_text());assert z['passed']and len(z['components'])==6 and all(q['passed']for q in z['components'].values())and z['additive_timing']['passed']
 b=scoped_load(a.run/'candidate.nes');assert sha(a.run/'candidate.nes')=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
 raw=b['raw'];lo,hi=location(b,'X5MenuCursorLo'),location(b,'X5MenuCursorHi');assert hi-lo==19
 cursor=[raw[lo+i]+256*raw[hi+i]for i in range(19)];name=address(b,'X5MenuNameAddress');assert name==0x2328
 rectangles=[]
 def cells(kind,at,n):
  assert 0x2000<=at and at+n<=0x23c0
  row,col=divmod(at-0x2000,32);assert col+n<=32
  q=dict(kind=kind,PPU_address=at,cells=n,rectangle_inclusive=[col*8,row*8,(col+n)*8-1,row*8+7]);rectangles.append(q)
 cells('authorized static20cell legend',0x2346,20);cells('selected16cell name from X5MenuNameAddress',name,16)
 for i,at in enumerate(cursor):cells('cursor index'+str(i)+' from linked X5MenuCursorLo/Hi',at,1)
 rectangles.append(dict(kind='conservative selected-player preview region, explicit non-oracle exclusion',rectangle_inclusive=[80,136,176,208]))
 mask=Image.new('L',(256,240),255);md=ImageDraw.Draw(mask)
 for q in rectangles:md.rectangle(tuple(q['rectangle_inclusive']),fill=0)
 included=mask.histogram()[255];excluded=61440-included;mask.save(a.output/'static-background-included-mask.png')
 refs=[185,200];ref_files=[baseline/f'frame-{n:06d}.argb'for n in refs];reference=image(ref_files[0]);validation=[]
 count,box,dm=mismatch(reference,image(ref_files[1]),mask)
 validation.append(dict(first_frame=refs[0],second_frame=refs[1],static_mismatches=count,bbox=box,passed=count==0))
 put(a.output/'reference-validation.json',validation)
 refsheet=Image.new('RGB',(768,260),'#202020');rd=ImageDraw.Draw(refsheet)
 for i,(label,im)in enumerate([('actual3cee185',reference),('actual3cee200',image(ref_files[1])),('included pixels white',mask.convert('RGB'))]):refsheet.paste(im,(256*i,20));rd.text((256*i,0),label,fill='white')
 refsheet.save(a.output/'two-baseline-references-and-mask.png')
 # Known actual b0 failures are positive rejection controls, never retagged.
 negatives=[]
 for n in [194,206,218,230,242,254,266]:
  f=bad/f'frame-{n:06d}.argb';cnt,bbox,_=mismatch(reference,image(f),mask);negatives.append(dict(frame=n,static_mismatches=cnt,bbox=bbox,expected_rejection=cnt>0,raw_sha256=sha(f)))
 put(a.output/'known-seven-b0-rejection-controls.json',negatives)
 owners=[];scope_enables=[]
 for line in(a.run/'menu-early-timing.jsonl').open():
  q=json.loads(line)
  if q['kind']=='early-menu-start-owner':owners.append(q)
  if q['kind']=='early-render-enable'and q['scope']and q['menu']==2 and q['oper']==0:scope_enables.append(q)
 assert len(owners)==z['additive_timing']['menu_start_owner_frames']
 hud={q['finished']['frame']:q for q in map(json.loads,(a.run/'hud-frames.jsonl').read_text().splitlines())}
 results=[];failed=[];bindings={}
 for q in owners:
  n=q['ppu']['frame'];f=a.run/f'frame-{n:06d}.argb';h=hud[n]['start']['ppu']
  assert(q['ppu']['cpu'],q['ppu']['frame'],q['ppu']['scanline'],q['ppu']['dot'])==(h['cpu'],h['frame'],h['scanline'],h['cycle'])
  assert len(q['nametables'])==4096 and len(q['actual_chr'])==12 and len(q['palette'])==32 and len(q['hardware_OAM'])==256
  im=image(f);cnt,bbox,diff=mismatch(reference,im,mask);equal=sha(f)==sha(baseline/f.name)
  item=dict(frame=n,selected=q['selected'],variant=q['variant'],PPU=q['ppu'],full_source_owner_snapshot=True,compared_static_pixels=included,excluded_pixels=excluded,static_mismatches=cnt,bbox=bbox,actual_frame_sha256=sha(f),same_frame3cee_raw_sha256=sha(baseline/f.name),same_frame_full_RGB_equal=equal,t=q.get('t'),v=q.get('v'),fineX=q.get('fineX'),w=q.get('w'))
  results.append(item);bindings[str(f)]=sha(f)
  if cnt:
   failed.append(item);im.save(a.output/f'failed-static-fullframe-{n:06d}.png');diff.save(a.output/f'failed-static-mask-{n:06d}.png')
 put(a.output/'all-owned-menu-static-pixels.json',results)
 ownerframes={q['ppu']['frame']for q in owners};missing=sorted({q['ppu']['frame']for q in scope_enables}-ownerframes)
 put(a.output/'scoped-enable-without-same-frame-start-owner.json',dict(frames=missing,explanation='A render enable can occur after startFrame; such frames do not have this exact early-start snapshot and are excluded from owner-bound pixel counts. They need separate actual wholeframe review, not invented ownership.'))
 # All observed-owned menu frames are shown, including full changed dynamic areas.
 pages=[]
 for page,start in enumerate(range(0,len(owners),30),1):
  group=owners[start:start+30];sheet=Image.new('RGB',(1536,1300),'#202020');sd=ImageDraw.Draw(sheet)
  for i,q in enumerate(group):
   n=q['ppu']['frame'];x,y=(i%6)*256,(i//6)*260;sheet.paste(image(a.run/f'frame-{n:06d}.argb'),(x,y+20));sd.text((x,y),str(n)+' char'+str(q['selected'])+' var'+str(q['variant']),fill='white')
  f=a.output/f'all-owned-menu-wholeframes-{page:02d}.png';sheet.save(f);pages.append(dict(path=str(f.resolve()),sha256=sha(f),frames=[q['ppu']['frame']for q in group]))
 put(a.output/'whole-menu-review-pages.json',pages)
 # Extra frames whose render enable follows startFrame are preserved for manual
 # review even though no same-frame full source snapshot was acquired there.
 extra_pages=[]
 for page,start in enumerate(range(0,len(missing),30),1):
  group=missing[start:start+30];sheet=Image.new('RGB',(1536,1300),'#202020');sd=ImageDraw.Draw(sheet)
  for i,n in enumerate(group):
   f=a.run/f'frame-{n:06d}.argb';bindings[str(f)]=sha(f);x,y=i%6*256,i//6*260;sheet.paste(image(f),(x,y+20));sd.text((x,y),'enable-after-start '+str(n),fill='white')
  f=a.output/f'enable-after-start-wholeframes-{page:02d}.png';sheet.save(f);extra_pages.append(dict(path=str(f.resolve()),sha256=sha(f),frames=group))
 put(a.output/'extra-wholeframe-review-pages.json',extra_pages)
 source=P=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/source'
 source_files=[source/'src/x5_menu_layout.inc',source/'src/x5_menu_ui.s',source/'src/character_select.s',source/'src/menu_vram_budget.s']
 put(a.output/'source-derived-mask.json',dict(rectangles=rectangles,included_pixels=included,excluded_pixels=excluded,name_address=name,cursor_addresses=cursor,source={str(f):sha(f)for f in source_files},exact_static_legend_word='SELECT ALTERNATES   ',preview_box_is_conservative_exclusion=True,limits='Fixed static subset only. Dynamic name/cursor/legend and entire preview box are excluded; no validation of those pixels, body visibility or background hidden under those areas. No background reconstruction is claimed.'))
 for f in ref_files+[bad/f'frame-{n:06d}.argb'for n in [194,206,218,230,242,254,266]]+[a.run/'candidate.nes',a.run/'candidate.dbg',a.run/'lifecycle-proof.json',a.run/'menu-early-timing.jsonl',a.run/'hud-frames.jsonl',Path(__file__)]+source_files:bindings[str(f.resolve())]=sha(f)
 for f in a.output.iterdir():
  if f.is_file():bindings[str(f.resolve())]=sha(f)
 put(a.output/'manifest.json',bindings)
 proof=dict(passed=count==0 and all(q['expected_rejection']for q in negatives)and not failed,offline_native_artifact_review=True,native_launched=False,ROM_sha256=z['ROM_sha256'],baseline_ROM_sha256=sha(baseline/'candidate.nes'),baseline_reference_frames=refs,baseline_static_mismatches=count,known_seven_b0_frames_rejected=sum(q['expected_rejection']for q in negatives),observed_owned_menu_frames=len(results),static_pixels_per_frame=included,total_static_pixel_comparisons=included*len(results),excluded_pixels_per_frame=excluded,failed_frames=failed,enable_frames_without_same_start_owner=missing,full_wholeframe_pages=len(pages),agent_visual_review=False,manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(__file__),limits='Offline exact static-subset RGB check from actual3cee185; second actual3cee200 validates mask. Every observed-owned selection frame compared, seven known b0 wraps must reject. Separate dynamic/preview exclusions and start-off/enable-later frames are disclosed and manually reviewed. No fullBG/all-pixel/body-flicker/globaltiming/adoption verdict.')
 put(a.output/'proof.json',proof);print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
