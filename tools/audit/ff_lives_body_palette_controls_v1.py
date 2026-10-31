"""Actual cold lives queue/render deadline, source colors and owned helper ABI."""
from pathlib import Path
import csv,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_lives_scroll_diagnostic_v1 as D
import ff_current_ready_cold_controls_v2 as C
import ff_cold_preview_controls_v1 as UI
from check_tmnt_render_oa import address
H=C.H;O=R/'build/ff-lives-body-palette-v1';J=O/'joint';P=D.J
def commands(data):
 out=[];i=0
 while data[i]:
  n=1 if data[i+2]&64 else data[i+2]&63
  out.append(dict(address=data[i]*256+data[i+1],length_flags=data[i+2],data=data[i+3:i+3+n]));i+=3+n
 return out
def pixel_witness(b):
 old=json.loads((R/'build/ff-lives-scroll-diagnostic-v1/diagnostic.json').read_text())['opaque'][0]
 colors={int(k):tuple(v)for k,v in old['lives_original_role_RGB'].items()}
 row=next(r for r in csv.DictReader((D.N/'gameplay-OAM.csv').open())if int(r['frame'])==334)
 data=bytes.fromhex(row['records64hex']);parts=[data[i:i+4]for i in range(0,256,4)if data[i]<240 and data[i+1]<64 and data[i+2]&3==0]
 pixels=D.sprite_pixels(b['raw'],782,parts);im=D.Image.open(D.N/'source-jump.png').convert('RGB')
 assert len(pixels)==250 and all(im.getpixel(xy)==colors[v]for xy,v in pixels.items())
 bbox=[min(x for x,y in pixels),min(y for x,y in pixels),max(x for x,y in pixels),max(y for x,y in pixels)]
 transparent=[im.getpixel((x,y))for y in range(bbox[1],bbox[3]+1)for x in range(bbox[0],bbox[2]+1)if(x,y)not in pixels]
 green=[p for p in transparent if p[1]>p[0]and p[1]>p[2]]
 return dict(authenticated_physical_page=782,actual_logged_DMA_frame=334,PPU_screenshot_sha256=D.sha(D.N/'source-jump.png'),opaque_pixels=250,exact_original_RGB_matches=250,translation=[0,0],source_RGB=colors,bbox=bbox,transparent_pixels_showing_green_background=len(green),
  prior_diagnostic_negative='v1 wrongly treated gameplay-OAM.csv page=2 as physicalCHR; it is CPU DMA page2. Its low match is retained. Correct physical782 is proved here by complete250/250 unshifted original pixel equality.',no_palette_or_sprite_coordinate_change=True)
def helper_controls(b,seed):
 rows=[];cuts=[]
 for valid,flags in itertools.product([0,1],[48|i for i in range(256)if not i&48]):
  m=C.A.T.copy(seed)
  if not valid:m.ram[3][0x1fe0]^=1
  H.put(m,VRAM_Buffer1_Offset=30);m[address(b,'VRAM_Buffer1')+30]=0
  prior=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+30]);smc=bytes(m[0x15a:0x17b]);maps=m.rawtags[:]
  c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=flags);states=[]
  for i in range(5000):
   if c.pc==0x5b00:break
   if address(b,'FwLivesBodyColors')<=c.pc<address(b,'FwLivesBodyColors')+19:states.append((i,c.pc))
   c.step()
  else:raise AssertionError('helper return')
  assert (c.a,c.x,c.y,c.p&0xcf,c.sp)==(1,1,30,flags&0xcf,224)
  assert m.rawtags==maps and bytes(m[0x15a:0x17b])==smc
  assert list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+30])==prior
  assert H.get(m,'VRAM_Buffer1_Offset')==37
  packet=list(m[address(b,'VRAM_Buffer1')+30:address(b,'VRAM_Buffer1')+38]);assert packet==[63,16,4,15,22,48,54,0]
  if flags==48:cuts.extend((valid,step,pc)for step,pc in states)
  rows.append([valid,flags,c.processorCycles])
 # Every new helper instruction, real normal/lag NMI and IRQ, then original
 # caller completes. No synthetic register restore or mapper normalization.
 vectors=[]
 for valid,step,pc in cuts:
  for kind,lag in [('NMI',0),('NMI',255),('IRQ',255)]:
   m=C.A.T.copy(seed)
   if not valid:m.ram[3][0x1fe0]^=1
   H.put(m,VRAM_Buffer1_Offset=30,NmiDisable=lag);m[address(b,'VRAM_Buffer1')+30]=0
   c=H.start(m,'FwLivesColors',a=1,x=1,y=30,p=48)
   for _ in range(step):c.step()
   assert c.pc==pc
   z=C.A.V.interrupt(m,c,kind);H.finish(m,c);vectors.append(dict(valid=valid,pc=pc,kind=kind,lag=lag,**z))
 return dict(all64_live_flags_cold_and_valid=len(rows),rows=rows,actual_vectors=len(vectors),vector_rows=vectors)
def main():
 out=O/'controls.json';assert not out.exists();q=dict(passed=False,source_CPU=True,native=False,checks={})
 try:
  H.O=J;b=H.C.qualified(J/'candidate.nes');rows=[];first=[];seed=[];original=C.A.consume
  def consume(m):
   if H.get(m,'ScreenRoutineTask')==7 and H.get(m,'VRAM_Buffer1_Offset'):
    data=list(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]);cmd=commands(data)
    assert H.get(m,'VRAM_Buffer1_Offset')==37 and [r['address']for r in cmd]==[0x23dc,0x21cd,0x214b,0x220c,0x3f10],cmd
    # Correct repeat-aware parser: native 220C command is a seven-space
    # repeat, not seven following palette bytes.
    assert cmd[-1]==dict(address=0x3f10,length_flags=4,data=[15]+([22,48,54]if H.get(m,'FfVariant')<2 else[40,24,33]))
    pre=list(m.vram[0x3f14:0x3f20]);z=D.nmi_trace(m);post=list(m.vram[0x3f14:0x3f20]);assert pre==post,'Lives only modifies native universal/bodyP0'
    mask=[r for r in z['events']if r['address']==0x2001 and r['value']&24]
    assert len(mask)==1;nominal=mask[0]['cycle']+z['nominal_DMA_addend'];assert nominal<2360,nominal
    body=UI.exact_body(m);assert all(p[2]&3==0 for p in body['OAM'])
    rows.append(dict(variant=H.get(m,'FfVariant'),queue_offset=37,commands=cmd,body=body,nominal_render_enable_CPU=nominal,trace=z))
    if not seed and H.get(m,'FfVariant')==1:seed.append(C.A.T.copy(m))
    return dict(real_NMI=z)
   return original(m)
  C.A.consume=consume
  try:q['checks']['actual_four_cold_parser_128_Main_TOTAL']=C.four_classes(b)
  finally:C.A.consume=original
  assert {r['variant']for r in rows}==set(range(4));q['checks']['all_four_actual_first_lives']=rows
  q['checks']['owned_helper_ABI_full_cookie_and_real_vectors']=helper_controls(b,seed[0])
  q['checks']['native_white_mage_opaque_palette_witness']=pixel_witness(b)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):D.sha(p)for p in[Path(__file__),Path(D.__file__),Path(C.__file__),Path(UI.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',D.N/'lives.png',D.N/'source-jump.png',D.N/'gameplay-OAM.csv']}
 out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),path=str(out))),flush=True);assert q['passed']
if __name__=='__main__':main()
