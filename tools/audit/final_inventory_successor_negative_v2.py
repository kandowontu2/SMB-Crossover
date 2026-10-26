"""Read-only final3b gallery firstFALSE, source refill model and actual pixel chronology; retains initial unflushed112 HUD."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
from final_inventory_successor_gallery_run_v1 import SHA,ROOT,verify_manifest
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA;count=verify_manifest(a.ready/'manifest.json')
 native=Path(next(q['output']for q in ready['profiles']if q['profile']=='bass-easy'));hard=Path(next(q['output']for q in ready['profiles']if q['profile']=='bass-hard'));assert not(hard/'launch.json').exists()
 proof=json.loads((native/'proof.json').read_text());assert proof['passed']is False and proof['runner_exit']==1 and proof['dependencies_unchanged']
 failure=json.loads((native/'first-failure.json').read_text());assert failure['message']=='Funded source actions exhaust exact seeded stock'and failure['phase']==dict(name='kick-face1',phase='funded')
 cfg=json.loads((native/'config.json').read_text());frames=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')));assert len(frames)==3759 and (native/'actual-ppu.argb').stat().st_size==len(frames)*245760
 events=[json.loads(s)for s in(native/'events.jsonl').read_text().splitlines()];caps=[q for q in events if q['kind']=='ppu-frame-captured'];bycase={i:[q for q in events if q['case']==i]for i in range(1,12)}
 spend=next(q for q in bycase[11]if q['kind']=='actual-source-spend');contact=next(q for q in bycase[11]if q['kind']=='actual-source-contact')
 assert spend['data']['before']==4 and spend['data']['after']==0 and spend['data']['item']==5 and spend['data']['cost']==4 and spend['wall']==3555
 assert contact['data']['ammo']==0 and contact['wall']==3559 and contact['data']['kick']==contact['data']['dash']==1
 put(a.output/'case11-events.json',bycase[11]);put(a.output/'all-source-events.json',events)
 dma=starts=pending=enables=0;last=None;hashes=[];minimum=10000
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==dma+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']and len(q['writes'])==256
   assert q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0 for i,w in enumerate(q['writes']))
   dma+=1;last=q;hashes.append(dict(id=dma,source_sha256=digest(bytes(q['source'])),hardware_sha256=digest(bytes(q['hardware']))))
  elif q['kind']=='startFrame-hardware':
   starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==last['source']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   enables+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
   if s['scanline']==-1:minimum=min(minimum,274-s['cycle'])
 assert(dma,starts,pending,enables)==(3150,3759,3,2897);put(a.output/'all-complete-DMA-hashes.json',hashes)
 # Real assembled source refill. This is CPU ownership evidence, not a new native run.
 b=scoped_load(native/'candidate.nes');refills=[]
 for amount in[8,40]:
  q=Arena(b,9);q.put(CrossoverBehaviorVersion=0,DisableScreenFlag=0,InvDirty=0,InvRefill=0,InvRefillRemain=0)
  q.set('InvSelected',5,9);q.set('InvOwnedLo',255,9);q.set('InvOwnedHi',0,9);q.set('InvAmmo',0,149)
  q.invoke('InventoryRefillAmount',a=amount);assert q.get('InvRefill')==149 and q.get('InvRefillRemain')==amount and q.get('InvRefillTick')==3
  changes=[];old=0
  for update in range(1,amount//4*3+1):
   q.put(VRAM_Buffer1_Offset=0);q.set('VRAM_Buffer1',0);_,trace=q.invoke('InventoryUiTick');value=q.get('InvAmmo',149)
   if value!=old:
    writes=[w for w in trace if w['address']==address(b,'InvAmmo')+149];assert len(writes)==1 and writes[0]['value']==value
    changes.append(dict(update=update,before=old,after=value,writer=writes[0]));old=value
  assert old==amount and q.get('InvRefill')==0 and [q['update']for q in changes]==list(range(3,amount//4*3+1,3))
  refills.append(dict(amount=amount,selected_item=5,actual_index=149,changes=changes,final_stock=old,final_refill=0))
 put(a.output/'compiled-refill-controls.json',dict(passed=True,ROM_sha256=SHA,controls=refills,scope='Actual InventoryRefillAmount then full InventoryUiTick CPU execution; explicit selected/owned/stock seeds. Does not claim native first refill writer was instrumented.'))
 raw=(native/'actual-ppu.argb').open('rb');font=cfg['diagnostic']['CHR_offset'];rom=(native/'candidate.nes').read_bytes()
 def data(n):raw.seek((n-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 def image(n):return Image.frombytes('RGBA',(256,240),data(n),'raw','BGRA').convert('RGB')
 def tile(page,t):
  z=rom[font+page*1024+t*16:font+page*1024+t*16+16];return [((z[y]>>(7-x))&1)|(((z[y+8]>>(7-x))&1)<<1)for y in range(8)for x in range(8)]
 def cell(im,x,y):return list(im.crop((x,y,x+8,y+8)).getdata())
 def color_map(im,page,ids,xy):
  mapping=collections.defaultdict(set)
  for t,(x,y)in zip(ids,xy):
   for k,v in zip(tile(page,t),cell(im,x,y)):mapping[k].add(v)
  assert all(len(v)==1 for v in mapping.values()),dict(mapping)
  z={k:next(iter(v))for k,v in mapping.items()};assert len(set(z.values()))==len(z);return z
 # Recover resource text from source digit bitmaps, not OCR or an assumed stock counter.
 kick=cfg['cases'][10];chron=[];lastvalue=None
 for n in range(3550,3760):
  im=image(n);m=color_map(im,240,kick['hud_name'],[(24+i*8,8)for i in range(7)]);digits=[]
  for i in range(3):
   actual=cell(im,88+i*8,8);matches=[t for t in range(10)if actual==[m[k]for k in tile(240,t)]];assert len(matches)==1,(n,i,matches);digits.append(matches[0])
  value=digits[0]*100+digits[1]*10+digits[2]
  if value!=lastvalue:chron.append(dict(ordinal=n,actual_PPU=frames[n-1],HUD_stock=value,digit_tiles=digits,raw_slice_sha256=digest(data(n)),palette_index_to_actual_RGB=m));lastvalue=value
 assert [q['HUD_stock']for q in chron]==[112,4,0,4,8,12,16,20,24,28,32,36,40],chron
 put(a.output/'actual-kick-resource-pixel-chronology.json',dict(passed=True,rows=chron,method='Source exact name/digit 2bpp bitmaps against every actual3550..3759 fullPPU frame; name provides current palette-index/color anchors; no RGB background reconstruction or native RAM write assertion.'))
 derived=[];lastcaps={q['data']['name']:q for q in caps}
 for name,q in lastcaps.items():assert(native/(name+'.argb')).read_bytes()==data(q['wall'])
 def save(n,label,reason,case=0):
  f=a.output/'frames'/(label+'.png');f.parent.mkdir(exist_ok=True);image(n).save(f);z=dict(path=str(f),sha256=sha(f),raw_slice_sha256=digest(data(n)),ordinal=n,actual_PPU=frames[n-1],reason=reason,case=case);derived.append(z);return z
 for i,q in enumerate(caps,1):save(q['wall'],f'{i:03}-{q["data"]["name"]}',dict(kind='exact original case capture',source_event=q),q['case'])
 extra=sorted(set([q['ordinal']for q in chron]+[3556,3559,3560,3561,3562,3563,3564,3565,3566,3758,3759]))
 for n in extra:save(n,f'kick-context-{n:06}',dict(kind='funded contact/refill/final completed prefix context'),11)
 # Selected name and icon pixel-index consistency against actual ROM font pages.
 glyphs=[]
 for q in caps:
  if not q['data']['name'].endswith('-selected-HUD'):continue
  c=cfg['cases'][q['case']-1];im=image(q['wall']);page=c['icon_bank']or 236;m=color_map(im,page,c['hud_name'],[(24+i*8,8)for i in range(7)])
  row=dict(case=q['case'],name=c['name'],ordinal=q['wall'],actual_PPU=frames[q['wall']-1],page=page,seven_name_tiles_exact_palette_index_classes=True,name_color_classes=m)
  if c['item']:
   icon=color_map(im,page,[42,43,44,45],[(184,8),(192,8),(184,16),(192,16)]);assert icon[0]==m[0]and icon[1]==m[1];row.update(actual16x16icon_source_pixel_index_classes_exact=True,icon_color_classes=icon)
  else:
   for x,y in[(184,8),(192,8),(184,16),(192,16)]:assert len(set(cell(im,x,y)))==1 and cell(im,x,y)[0]==m[0]
   row.update(actual_default_icon_blank=True)
  glyphs.append(row)
 assert len(glyphs)==11;put(a.output/'actual-selected-HUD-glyph-pixels.json',dict(passed=True,cases=glyphs,scope='All eleven observed selected-HUD names/icons checked at source-derived coordinates against immutable 2bpp font tiles and consistent distinct actual RGB classes. Palette color values are actual captured classes, not an independent NES palette/RGB model.'))
 put(a.output/'frame-selection.json',derived);sheets=[]
 for case in range(1,12):
  rows=[q for q in derived if q['case']==case]
  for start in range(0,len(rows),12):
   entries=rows[start:start+12];im=Image.new('RGB',(4*272,3*280),(32,32,32));draw=ImageDraw.Draw(im);placements=[]
   for i,q in enumerate(entries):
    x=i%4*272;y=i//4*280;im.paste(Image.open(q['path']),(x,y+32));draw.text((x+2,y+1),f'PPU {q["actual_PPU"]["ppu_frame"]} / ordinal {q["ordinal"]}',fill='white');draw.text((x+2,y+15),Path(q['path']).stem[:38],fill='white');placements.append(dict(x=x,y=y+32,width=256,height=240,frame=q))
   f=a.output/f'case-{case:02}-whole-PPU-{start//12+1:02}.png';im.save(f);sheets.append(dict(path=str(f),sha256=sha(f),case=case,placements=placements))
 put(a.output/'sheets.json',sheets)
 observed={i:dict(collections.Counter(q['kind']for q in z))for i,z in bycase.items()};cleaned=[i for i,z in bycase.items()if any(q['kind']=='gallery-phase'and q['phase']=='next'for q in z)]
 result=dict(passed=False,preservation_passed=True,ROM_sha256=SHA,native_proof_sha256=sha(native/'proof.json'),native_aggregate_remains_FALSE=True,Hard_unrun=True,native_worker_released=True,ready_bindings_verified=count,actual_numeric_mode=0,completed_PPU_frames=len(frames),raw_bytes=(native/'actual-ppu.argb').stat().st_size,complete256DMAs=dma,data_writes=dma*256,startFrames=starts,pending_starts=pending,safe_scoped_enables=enables,pre_render_minimum_dot_margin=minimum,first_failure=failure,source_event_counts=observed,case_capture_events=len(caps),unique_case_capture_names=len(lastcaps),case_files_match_last_raw_capture=True,selection_placements=len(derived),sheets=len(sheets),agent_visual_review=False,conclusion='KICK is activated/paid/contacted correctly, then observed HUD refills0to40 after controlled enemy defeat. Final zero-stock assertion is confounded by allowed native earned capsule/refill; no game defect established.',first_native_refill_RAM_writer_observed=False,limits=['No native success summary or full16case qualification; originalFALSE remains.','First ten cases reached source component phases before case11 stop; no second KICK/FLAME/WATER gallery qualification and no Hard run.','Resource/arena/target seeds are B-only. Native enemy drop and collection were not disabled; no RNG injection.','Raw diagnostic850..950 does not cover KICK3759; actual first refill RAM/drop writer and RNG roll are unobserved.','Source-aligned 0to40 refill CPU model and exact actual HUD chronology support a fixture expectation error, not a causal native first-write trace.','Prior945/1630 deadline faults absent only in this observed prefix; no global NMI worstcase/FPS claim.','Hardware source/CHR checks and selected glyph checks do not establish every sprite pixel/source fidelity or waveform; ARM questionblock and BALANCE remain missing.'])
 put(a.output/'analysis.json',result)
 files=set(f for f in native.iterdir()if f.is_file());files.update(f for f in a.output.rglob('*')if f.is_file());files.update([Path(__file__),a.ready/'proof.json',a.ready/'manifest.json'])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=False,preservation_passed=True,ROM_sha256=SHA,analysis_sha256=sha(a.output/'analysis.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),native_worker_released=True,Hard_unrun=True,agent_visual_review=False));verify_manifest(a.output/'manifest.json')
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),analysis=result),indent=2))
if __name__=='__main__':main()
