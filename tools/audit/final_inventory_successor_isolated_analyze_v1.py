"""Independent actual fullDMA/capsule ledger/source HUD pixel review preparation; read-only native input."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
from final_inventory_successor_gallery_run_v1 import SHA,verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda p:hashlib.sha256(p).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=['bass-easy','bass-hard'],required=True);p.add_argument('--summary-read',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA;bindings=verify_manifest(a.ready/'manifest.json');native=Path(next(q['output']for q in ready['profiles']if q['profile']==a.profile));proof=json.loads((native/'proof.json').read_text());assert proof['runner_exit']==0 and proof['dependencies_unchanged']and not(native/'first-failure.json').exists()
 interpreted=json.loads((a.summary_read/'proof.json').read_text());assert interpreted['passed']and interpreted['native_execution_passed']and interpreted['original_collector_proof_sha256']==sha(native/'proof.json')and interpreted['lossless_reversal_passed']
 assert sha(a.summary_read/'native-summary-normalized.json')==interpreted['normalized_summary_sha256']
 cfg=json.loads((native/'config.json').read_text());mode=int(a.profile=='bass-hard');assert cfg['mode_value']==mode;summary=json.loads((a.summary_read/'native-summary-normalized.json').read_text());assert summary['passed']and summary['actual_mode_readback']==mode and len(summary['cases'])==16 and summary['acquisition']is False
 events=[json.loads(s)for s in(native/'events.jsonl').read_text().splitlines()];caps=[q for q in events if q['kind']=='ppu-frame-captured'];frames=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')));assert(native/'actual-ppu.argb').stat().st_size==len(frames)*245760 and [int(q['ordinal'])for q in frames]==list(range(1,len(frames)+1))and all(int(q['mode'])==mode for q in frames if int(q['updates'])>0)
 counters=collections.Counter();completed=last=None;hashes=[];minimum=10000
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line);counters[q['kind']]+=1
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==len(hashes)+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']and len(q['writes'])==256
   assert q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0 for i,w in enumerate(q['writes']))
   last=q;hashes.append(dict(id=q['id'],source_sha256=digest(bytes(q['source'])),hardware_sha256=digest(bytes(q['hardware']))))
  elif q['kind']=='startFrame-hardware':
   assert len(q['hardware'])==256;counters['pending-starts']+=bool(q.get('pending_dma_id'))
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==last['source']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   counters['safe-scoped-enables']+=1;s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
   if s['scanline']==-1:minimum=min(minimum,274-s['cycle'])
 assert len(hashes)>100 and counters['safe-scoped-enables']>100 and counters['startFrame-hardware']>100
 put(a.output/'all-complete-DMA-hashes.json',hashes)
 ledgers=[]
 for case,c in enumerate(cfg['cases'],1):
  es=[q for q in events if q['case']==case];funded=[q for q in es if q['phase']=='funded'];spends=[q for q in funded if q['kind']=='actual-source-spend'];direct=[q for q in funded if q['kind']=='actual-pharaoh-direct-debit'];zeros=[q for q in funded if q['kind']=='actual-funded-debit-zero'];credits=[q for q in funded if q['kind']=='actual-funded-refill-credit'];resets=[q for q in es if q['kind']=='isolated-native-boundary-component-reset'];end=next(q for q in es if q['kind']=='gallery-phase'and q['phase']=='setup-empty')
  assert [q['data']['kind']for q in resets]==['funded','empty','pool']and any(q['kind']=='gallery-phase'and q['phase']=='clear-after-pool'for q in es)
  assert all(q['data']['after']==q['data']['before']-q['data']['cost']if q['data']['accepted']else q['data']['after']==q['data']['before']for q in spends)
  for q in direct:
   z=q['data'];admitted=z['shot_age']>=45 and z['active_shots']<2 and z['star']==0;assert z['paid_path']==admitted and z['after']==(max(0,z['before']-8)if admitted else z['before'])and z['actual_spent']==z['before']-z['after']
  for q in funded:
   if q['kind']=='actual-pharaoh-release-full-return':
    z=q['data'];entry=z['entry'];assert entry['pc']==0xaa96 and entry['bank']==60 and z['return_bank']==60 and z['return_sp']==(entry['sp']+2)%256
    raw=(native/'candidate.nes').read_bytes();off=16+60*8192+(z['return_pc']-3)%8192;assert raw[off:off+3]==bytes([0x20,0xe0,0xa7]),'Actual full return belongs to genuine compiled JSR SpecialWeapons::Motion'
  if c['item']==4:assert direct and any(q['kind']=='actual-pharaoh-release-full-return'for q in funded)
  else:assert not direct
  paid=sum(q['data']['cost']for q in spends if q['data']['accepted'])+sum(q['data']['actual_spent']for q in direct);earned=sum(q['data']['amount']for q in credits)
  if c['item']:
   assert zeros and paid>=c['initial_stock']and all(q['data']['after']==0 and q['data']['before']==q['data']['cost']for q in zeros)
   assert end['data']['ammo']==c['initial_stock']-paid+earned
  else:assert not zeros and not credits
  assert all(q['data']['index']==144+c['item']and q['data']['after']==min(112,q['data']['before']+4)and q['data']['remaining_after']==q['data']['remaining_before']-4 for q in credits)
  assert next(q for q in es if q['kind']=='gallery-phase'and q['phase']=='empty')['data']['ammo']==0
  assert all(q['type']==0 for q in next(q for q in es if q['kind']=='gallery-phase'and q['phase']=='empty')['data']['shots'])
  # change('next') follows the original index increment, but current's data is
  # the completed prior case. Bind that actual state without rewriting events.
  cleanup=next(q for q in events if q['case']==case+1 and q['kind']=='gallery-phase'and q['phase']=='next');cs=cleanup['data'];assert cs['held']==0 and all(q['type']==0 for q in cs['shots'])
  assert cs['kick']==0 or cs['kick']==2 and cs['selected']!=5 and cs['dash']!=0
  ledgers.append(dict(case=case,name=c['name'],funded_seed=c['initial_stock'],actual_funded_paid=paid,actual_earned_credit=earned,actual_end_funded_stock=end['data']['ammo'],zero_witnesses=zeros,source_spends=spends,direct_Pharaoh_spends=direct,full_Pharaoh_returns=[q for q in funded if q['kind']=='actual-pharaoh-release-full-return'],refill_credits=credits,reset_disclosures=resets,source_contact=[q for q in es if q['kind']=='actual-source-contact'],selection_and_cleanup=[q for q in es if q['kind']=='gallery-phase'],actual_full_update_cleanup_state=cleanup))
 put(a.output/'actual-capsule-debit-credit-ledger.json',dict(passed=True,rows=ledgers,scope='Read-only actual event ledger. Paidzero witness and earnedUiTick credits are native; clearing old drops/explicit zero-refusal happen only at logged B setup boundaries. Final current-record accounting fields are reset by later components, so per-phase events are authoritative.'))
 raw=(native/'actual-ppu.argb').open('rb');rom=(native/'candidate.nes').read_bytes();font=cfg['diagnostic']['CHR_offset']
 def data(n):raw.seek((n-1)*245760);v=raw.read(245760);assert len(v)==245760;return v
 def image(n):return Image.frombytes('RGBA',(256,240),data(n),'raw','BGRA').convert('RGB')
 def tile(page,t):
  z=rom[font+page*1024+t*16:font+page*1024+t*16+16];return [((z[y]>>(7-x))&1)|(((z[y+8]>>(7-x))&1)<<1)for y in range(8)for x in range(8)]
 def cell(im,x,y):return list(im.crop((x,y,x+8,y+8)).getdata())
 def classes(im,page,ids,xy):
  m=collections.defaultdict(set)
  for t,(x,y)in zip(ids,xy):
   for k,v in zip(tile(page,t),cell(im,x,y)):m[k].add(v)
  assert all(len(v)==1 for v in m.values()),dict(m);z={k:next(iter(v))for k,v in m.items()};assert len(set(z.values()))==len(z);return z
 glyphs=[]
 for case,c in enumerate(cfg['cases'],1):
  event=next(q for q in caps if q['data']['name']==c['name']+'-selected-HUD');n=event['wall'];im=image(n);page=c['icon_bank']or 236;m=classes(im,page,c['hud_name'],[(24+i*8,8)for i in range(7)]);row=dict(case=case,name=c['name'],ordinal=n,actual_PPU=frames[n-1],page=page,name_tiles_exact=True,name_color_classes=m)
  if c['item']:
   icon=classes(im,page,[42,43,44,45],[(184,8),(192,8),(184,16),(192,16)]);assert icon[0]==m[0]and icon[1]==m[1];row.update(icon_source_index_classes_exact=True,icon_color_classes=icon)
  else:
   for x,y in[(184,8),(192,8),(184,16),(192,16)]:assert set(cell(im,x,y))=={m[0]}
   row['default_icon_blank']=True
  glyphs.append(row)
 put(a.output/'actual-selected-HUD-glyph-pixels.json',dict(passed=True,rows=glyphs,scope='Sixteen actual selected-HUD names/icons vs immutable source2bpp pixel classes at sourcecoordinates. Actual RGB classes must be distinct/consistent; not an independent NES palette model or allbackground/pixel fidelity.'))
 # Every actual case capture is bound to its fullraw slice; originals match the last reuse.
 lastcaps={q['data']['name']:q for q in caps}
 for name,q in lastcaps.items():assert(native/(name+'.argb')).read_bytes()==data(q['wall'])
 capture_index=[dict(event=q,raw_slice_sha256=digest(data(q['wall'])))for q in caps];put(a.output/'all-case-capture-events.json',capture_index)
 derived=[];sheets=[]
 for case,c in enumerate(cfg['cases'],1):
  # The original queued endFrame capture may be emitted after index advances.
  # Its unique source-case name is authoritative, not the then-current index.
  cs=[q for q in caps if q['data']['name'].startswith(c['name']+'-')];selected=[]
  suffixes=['-selected-HUD','-funded-setup','-contact','-natural-cleanup','-exhaust-refusal','-selection-cleanup']
  for suffix in suffixes:
   q=next(q for q in cs if q['data']['name']==c['name']+suffix);selected.append((q['wall'],q['data']['name'],dict(kind='actual original source-case capture',event=q)))
  for q in cs:
   if '-art-'in q['data']['name']:selected.append((q['wall'],q['data']['name'],dict(kind='actual first effect-art owner capture',event=q)))
  zeros=[q for q in cs if '-actual-debit-zero'in q['data']['name']]
  if zeros:q=zeros[-1];selected.append((q['wall'],q['data']['name'],dict(kind='actual accepted zero-debit publication',event=q)))
  pools=[q for q in cs if q['data']['name'].endswith('-pool-refusal')or q['data']['name'].endswith('-pool-setup')];q=pools[-1];selected.append((q['wall'],q['data']['name'],dict(kind='actual controlled fullpool policy',event=q)))
  credits=[q for q in cs if '-earned-credit-'in q['data']['name']]
  if credits:q=credits[-1];selected.append((q['wall'],q['data']['name'],dict(kind='actual last earned native credit',event=q)))
  entries=[]
  for n,label,reason in selected:
   f=a.output/'frames'/f'{case:02}-{label}.png';f.parent.mkdir(exist_ok=True);image(n).save(f);q=dict(path=str(f),sha256=sha(f),raw_slice_sha256=digest(data(n)),ordinal=n,actual_PPU=frames[n-1],reason=reason,case=case);entries.append(q);derived.append(q)
  for start in range(0,len(entries),12):
   chosen=entries[start:start+12];im=Image.new('RGB',(4*272,3*280),(32,32,32));draw=ImageDraw.Draw(im);placements=[]
   for i,q in enumerate(chosen):
    x=i%4*272;y=i//4*280;im.paste(Image.open(q['path']),(x,y+32));draw.text((x+2,y+1),f'PPU {q["actual_PPU"]["ppu_frame"]} / ordinal {q["ordinal"]}',fill='white');draw.text((x+2,y+15),Path(q['path']).stem[:38],fill='white');placements.append(dict(x=x,y=y+32,width=256,height=240,frame=q))
   f=a.output/f'case-{case:02}-whole-PPU-{start//12+1:02}.png';im.save(f);sheets.append(dict(path=str(f),sha256=sha(f),case=case,placements=placements))
 put(a.output/'frame-selection.json',derived);put(a.output/'sheets.json',sheets)
 analysis=dict(passed=True,raw_and_source_analysis_passed=True,agent_visual_review=False,ROM_sha256=SHA,native_proof_sha256=sha(native/'proof.json'),actual_numeric_mode=mode,plans=16,lane='B',acquisition=False,ready_bindings_verified=bindings,completed_PPU_frames=len(frames),raw_bytes=(native/'actual-ppu.argb').stat().st_size,raw_sha256=sha(native/'actual-ppu.argb'),index_sha256=sha(native/'actual-ppu-index.csv'),complete256DMAs=len(hashes),data_writes=len(hashes)*256,startFrame_snapshots=counters['startFrame-hardware'],pending_starts=counters['pending-starts'],safe_scoped_enables=counters['safe-scoped-enables'],minimum_pre_render_dot_margin=minimum,native_updates=summary['updates'],native_nmis=summary['nmis'],minSP=summary['minSP'],irq_scroll_stores=summary['irq_scroll_stores'],hardware_chr_checks=summary['hardware_chr_checks'],complete_dma_checks=summary['complete_dma_checks'],source_funded_credits=sum(q['actual_earned_credit']for q in ledgers),credit_cases=[q['name']for q in ledgers if q['actual_earned_credit']],zero_witness_cases=sum(bool(q['zero_witnesses'])for q in ledgers),case_capture_events=len(caps),unique_original_case_names=len(lastcaps),allcasefiles_match_last_raw_event=True,selected_placements=len(derived),sheets=len(sheets),native_worker_released=True,limits=['Mechanical/raw/source/glyph scope only until agent image review.','B-only seeded inventory/resources/arena/actors, no acquisition. ARMquestionblock/BALANCE excluded.','Paid/exhaustion witnesses and full source credit ledger do not claim naturally earned initial weapon stock.','All original failed native aggregates remain false and immutable. No fullroster/item/campaign/sourcefidelity/waveform/visibility/FPS/globalNMIworstcase claim.'])
 analysis.update(native_execution_passed=True,original_collector_passed=proof['passed'],summary_interpretation_path=str(a.summary_read),summary_interpretation_sha256=sha(a.summary_read/'proof.json'),machine_output_limit='Original collectorFALSE unchanged. Numeric object-key quoting is reversible; per-component emptyCheckedfalse remains, actual refusal event chronology independently checked.')
 put(a.output/'analysis.json',analysis);files=set(f for f in native.iterdir()if f.is_file());files.update(f for f in a.output.rglob('*')if f.is_file());files.update(f for f in a.summary_read.iterdir()if f.is_file());files.update([Path(__file__),Path(__file__).with_name('final_inventory_successor_summary_read_v1.py'),a.ready/'proof.json',a.ready/'manifest.json']);put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=True,raw_source_only=True,agent_visual_review=False,ROM_sha256=SHA,analysis_sha256=sha(a.output/'analysis.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),native_proof_sha256=sha(native/'proof.json'),original_collector_passed=proof['passed'],summary_interpretation_sha256=sha(a.summary_read/'proof.json'),native_worker_released=True));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),analysis=analysis),indent=2))
if __name__=='__main__':main()
