"""Prove real service17 title/lives draw, final CHR/OAM and unchanged gameplay."""
from pathlib import Path
import collections,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_current_ready_cold_controls_v2 as C
import ff_current_ready_regressions_v2 as G
from check_tmnt_render_oa import address,location
H=C.H;O=R/'build/ff-cold-preview-v3';P=R/'build/ff-current-names-v3';H.O=O/'joint'
def visible(m):return[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240]
def draw(m,name,**kw):
 points={}
 for n in['GmMenuDrawGate','HuMenuPortrait','FwPortrait','FwHostDrawShots','FwPortraitDraw','DrawMetasprite','MetaspriteRenderLoop','FwLoad','FwPreviewPublish','FfHostDrawShots']:
  if n in m.bundle['syms']:points[address(m.bundle,n),3 if n.startswith('Ff')else((location(m.bundle,n)-16)//8192)|128]=n
 events=[];before=m.rawtags[:];c=H.start(m,name,**kw);live=bytes(m[0x1e1:0x200])
 def hook(mem,c,i):
  if 0x8000<=c.pc<0xe000:
   tag=mem.rawtags[(c.pc-0x8000)//8192]
   if(c.pc,tag)in points:events.append([i,points[c.pc,tag],c.a,c.x,c.y,c.p,c.sp])
 c,low=H.finish(m,c,hook);assert c.sp==224 and bytes(m[0x1e1:0x200])==live
 assert m.rawtags[1]==before[1]and m.rawtags[2]==H.get(m,'CurrentBankC')
 return dict(AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minSP=low,events=events,counts=dict(collections.Counter(r[1]for r in events)))
def exact_body(m):
 at=address(m.bundle,'FfRenderBuffer');header=m[at];assert header and header<=32 and not header%4
 rec=bytes(m[at:at+header+1]);parts=visible(m);x=H.get(m,'Player_X_Position')-H.get(m,'ScreenLeft_X_Pos');y=H.get(m,'Player_Y_Position')
 def signed(n):return n-256 if n&128 else n
 want=[]
 for i in range(1,header+1,4):want.append([y+signed(rec[i+2]),rec[i],rec[i+1],x+signed(rec[i+3])])
 assert sorted(parts)==sorted(want),('native actual body0 OAM',parts,want)
 page=756+H.get(m,'FfRenderPage');assert m.chr_latches[0]==page,('actual final hardware body page',m.chr_latches[0],page)
 assert H.get(m,'FfTemp2')==0
 # Exact original patterns for every nontransparent source pixel. No atlas
 # copy, color reduction, or game code is used as CHR.
 raw=m.bundle['raw'];pixels=[]
 for sy,t,a,sx in parts:
  assert t<64
  for yy in range(16):
   py=15-yy if a&128 else yy;tile=(t&254)+py//8;pos=1048592+page*1024+tile*16+py%8
   for xx in range(8):
    px=7-xx if a&64 else xx;v=((raw[pos]>>(7-px))&1)|(((raw[pos+8]>>(7-px))&1)<<1)
    if v:pixels.append([sx+xx,sy+1+yy,m.vram[0x3f10+(a&3)*4+v]])
 assert pixels and all(p[2]in([0x16,0x30,0x36]if H.get(m,'FfVariant')<2 else[0x28,0x18,0x21])for p in pixels)
 return dict(OAM=parts,source_record=list(rec),physical_page=page,opaque_pixels=len(pixels),hardware_P0=list(m.vram[0x3f11:0x3f14]))
def main():
 out=O/'controls-v1.json';assert not out.exists();p=dict(passed=False,native=False,admitted=False,installed=False,checks={})
 try:
  b=H.C.qualified(O/'joint/candidate.nes');old=H.C.qualified(P/'joint/candidate.nes');rows=[];negative=[]
  for v,shadows in itertools.product(range(4),range(2)):
   for bundle,label in[(old,'parent'),(b,'successor')]:
    m=C.fresh(bundle,v);H.put(m,PlayerOutlinesOff=shadows);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
    before=[bytes(x)for x in m.ram];z=draw(m,'DrawSelectionPreview');C.A.consume(m)
    assert m.ppu_reads==0 and not m.ram_writes and[bytes(x)for x in m.ram]==before
    if label=='parent':assert not visible(m);negative.append(dict(variant=v,shadows=shadows,call=z))
    else:
     assert z['counts'].get('FwPortrait')==1 and z['counts'].get('FwPortraitDraw')==1
     assert z['counts'].get('DrawMetasprite')==1 and not z['counts'].get('FwHostDrawShots')
     rows.append(dict(variant=v,shadows=shadows,call=z,body=exact_body(m),no_cache_load_or_RAM3_execution=True))
  p['checks']['real_cold_Only17_original_body_pixels']=dict(rows=rows,parent_empty_OAM_negative=negative)
  # Real default gameplay row2 must stay untouched, including all branch
  # guards and source body/effect iterator. Full cold source sequence runs it.
  lives=[];orig=C.A.consume
  def consume(m):
   z=orig(m)
   if H.get(m,'OperMode')==1 and H.get(m,'ScreenRoutineTask')==7 and H.get(m,'FfReady')==247:
    body=exact_body(m);lives.append(dict(variant=H.get(m,'FfVariant'),body=body))
   return z
  C.A.consume=consume
  try:p['checks']['four_classes_actual_cold_Main']=C.four_classes(b)
  finally:C.A.consume=orig
  assert{r['variant']for r in lives}==set(range(4)),('all4 true native lives bodies',lives)
  p['checks']['real_lives_body0_final_hardware']=dict(rows=lives)
  menu=G.profiles(b);assert menu['ready_profiles']==58;p['checks']['actual80_profiles']=menu
  for row in menu['rows']:
   if row['slot']==21:assert len(row['visible_OAM'])>=4 and 756<=row['current_CHR'][0]<788
  p['passed']=True
 except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
 files={Path(__file__),Path(C.__file__),Path(G.__file__),O/'source-proof.json',O/'joint/candidate.nes',O/'joint/candidate.dbg',P/'joint/candidate.nes',P/'joint/candidate.dbg'}
 for module in list(sys.modules.values()):
  f=getattr(module,'__file__',None)
  if f and Path(f).resolve().is_relative_to(R/'tools'):files.add(Path(f).resolve())
 p['bindings']={str(f.resolve()):C.L.sha(f)for f in files if f.exists()};out.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps(dict(passed=p['passed'],error=p.get('error'),path=str(out))));assert p['passed']
if __name__=='__main__':main()
