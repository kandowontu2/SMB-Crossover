"""Read-only completed exactce635 MegaHard14 actual scope and review sheets."""
from pathlib import Path
import argparse, collections, csv, hashlib, json
from PIL import Image,ImageDraw
from final_megaproto_common_ce635_prepare_v1 import D,R,CAND as B,SHA
from final_megaproto_common_collector_witness_v1 import interpret_events
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def physical(s):return[v&0xe3 if i%4==2 else v for i,v in enumerate(s)]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 r=json.loads((a.ready/'proof.json').read_text());assert r['ROM_sha256']==SHA;verified=verify_manifest(a.ready/'manifest.json');n=Path(r['output']);np=json.loads((n/'proof.json').read_text());assert np['passed']and np['runner_exit']==0 and np['dependencies_unchanged']and not(n/'first-failure.json').exists();cfg=json.loads((n/'config.json').read_text());z=json.loads((n/'native-megaproto-common.json').read_text());assert z['passed']and z['actual_mode_readback']==1 and z['hard']is True and z['family']=='megaman'and z['acquisition']is False and len(z['cases'])==14
 assert[q['q']['name']for q in z['cases']]==[q['name']for q in cfg['cases']]
 assert all(q['naturalCleanup']and q['poolPassed']and q['selectionCleanup']and q['hits']>0 and q['damageCalls']>0 for q in z['cases'])
 assert z['nmis']>100 and z['irq_scroll_stores']>100 and z['hardware_chr_checks']>1200 and z['complete_dma_checks']>100 and z['minSP']>=128
 capture=json.loads((n/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert capture['passed']and capture['original_done_seen']and capture['actual_mode_readback']==1 and capture['frames']==len(rows)and capture['bytes']==(n/'actual-ppu.argb').stat().st_size==len(rows)*245760
 assert[int(q['ordinal'])for q in rows]==list(range(1,len(rows)+1))and all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
 counters=collections.Counter();hashes=[];last=None;literal=ignored_DMAs=ignored_bytes=matched=0
 for s in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(s);counters[q['kind']]+=1
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==len(hashes)+1 and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and physical(q['source'])==q['hardware']and not q['implemented_differences']
   assert q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0 for i,w in enumerate(q['writes']))
   diff=[dict(offset=i,source=x,hardware=y)for i,(x,y)in enumerate(zip(q['source'],q['hardware']))if x!=y];assert diff==list(q['differences'])==list(q['ignored_attribute_differences']);literal+=not diff;ignored_DMAs+=bool(diff);ignored_bytes+=len(diff);matched+=q['source_publication_match'];last=q;hashes.append(dict(id=q['id'],source_sha256=digest(bytes(q['source'])),hardware_sha256=digest(bytes(q['hardware'])),ignored=diff))
  elif q['kind']=='startFrame-hardware':
   assert len(q['hardware'])==256;counters['pending_starts']+=bool(q.get('pending_dma_id'))
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==last['hardware']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:assert q['safe'];counters['safe_enables']+=1
 put(a.output/'all-DMA-hashes.json',hashes)
 events=[json.loads(s)for s in(n/'events.jsonl').open()];independent_witnesses=interpret_events(events,cfg,z);assert independent_witnesses==np['analysis']['components']['ordered_case_witnesses'];caps=[q for q in events if q['kind']=='ppu-frame-captured'];ledger=[];b=scoped_load(n/'candidate.nes');assert sha(n/'candidate.nes')==SHA
 for case,c in enumerate(cfg['cases'],1):
  es=[q for q in events if q['case']==case];phases=[q for q in es if q['kind']=='gallery-phase'];funded=[q for q in es if q['phase']=='funded'];spends=[q for q in funded if q['kind']=='actual-source-spend'];direct=[q for q in funded if q['kind']=='actual-pharaoh-direct-debit'];credits=[q for q in funded if q['kind']=='actual-funded-refill-credit'];zeros=[q for q in funded if q['kind']=='actual-funded-debit-zero'];end=next(q for q in phases if q['phase']=='setup-empty')
  for q in spends:assert q['data']['after']==q['data']['before']-(q['data']['cost']if q['data']['accepted']else 0)
  for q in direct:
   d=q['data'];paid=d['shot_age']>=45 and d['active_shots']<2 and d['star']==0;assert d['paid_path']==paid and d['after']==(max(0,d['before']-8)if paid else d['before'])and d['actual_spent']==d['before']-d['after']
  returns=[q for q in funded if q['kind']=='actual-pharaoh-release-full-return']
  if c['item']==4:
   assert direct and returns
   for q in returns:
    d=q['data'];e=d['entry'];assert e['pc']==cfg['hooks']['SpecialWeapons::ReleaseBalloon']['address']and e['bank']==d['return_bank']==60 and d['return_sp']==(e['sp']+2)%256;off=16+60*8192+(d['return_pc']-3)%8192;assert b['raw'][off:off+3]==bytes([0x20,address(b,'SpecialWeapons::Motion')&255,address(b,'SpecialWeapons::Motion')>>8])
  else:assert not direct and not returns
  paid=sum(q['data']['cost']for q in spends if q['data']['accepted'])+sum(q['data']['actual_spent']for q in direct);earned=sum(q['data']['amount']for q in credits);assert zeros and paid>=c['initial_stock']and end['data']['ammo']==c['initial_stock']-paid+earned
  assert all(q['data']['after']==0 and q['data']['before']==q['data']['cost']for q in zeros)
  for q in credits:assert q['data']['index']==16+c['item']and q['data']['after']==min(112,q['data']['before']+4)and q['data']['remaining_after']==q['data']['remaining_before']-4
  empty=next(q for q in phases if q['phase']=='empty');end_empty=next(q for q in phases if q['phase']=='setup-pool');assert end_empty['update']-empty['update']==25
  for q in[empty,end_empty]:assert q['data']['ammo']==0 and q['data']['held']==0 and q['data']['kick']!=1 and all(s['type']==0 for s in q['data']['shots'])
  assert not[q for q in es if q['phase']=='empty'and q['kind']=='actual-special-spawn'];assert not[q for q in es if q['phase']=='empty'and q['kind']=='actual-source-spend'and q['data']['accepted']]
  cleanup=next(q for q in events if q['case']==case+1 and q['kind']=='gallery-phase'and q['phase']=='next');d=cleanup['data'];assert d['held']==0 and all(s['type']==0 for s in d['shots']);assert d['kick']==0 or d['kick']==2 and d['selected']!=5 and d['slide']!=0
  cs=[q for q in caps if q['data']['name'].startswith(c['name']+'-')];refusal=next(q for q in cs if q['data']['name']==c['name']+'-exhaust-refusal');assert refusal['update']==end_empty['update']and refusal['wall']>end_empty['wall']
  pool=[q for q in es if q['kind']in['actual-full-pool-refusal','actual-full-pool-special']];assert len(pool)==1
  assert[q['data']['kind']for q in es if q['kind']=='isolated-native-boundary-component-reset']==['funded','empty','pool']
  ledger.append(dict(case=case,name=c['name'],funded_seed=c['initial_stock'],native_paid=paid,native_credit=earned,funded_end=end['data']['ammo'],source_spends=spends,direct_Pharaoh=direct,full_Pharaoh_returns=returns,zero_witnesses=zeros,credits=credits,empty_entry=empty,empty_exit=end_empty,postassert_refusal_capture=refusal,pool=pool[0],cleanup=cleanup,raw_terminal_emptyChecked=z['cases'][case-1]['emptyChecked']))
 put(a.output/'actual-case-ledger.json',dict(passed=True,rows=ledger,scope='Actual native debit/contact/phase/refusal/pool/cleanup witnesses. Raw terminal emptyChecked retained; no missing refusal is masked by terminal presence. B-only complete setup, not acquisition.'))
 raw=(n/'actual-ppu.argb').open('rb')
 def data(i):raw.seek((i-1)*245760);v=raw.read(245760);assert len(v)==245760;return v
 def image(i):return Image.frombytes('RGBA',(256,240),data(i),'raw','BGRA').convert('RGB')
 lastcaps={q['data']['name']:q for q in caps}
 for name,q in lastcaps.items():assert(n/(name+'.argb')).read_bytes()==data(q['wall'])
 put(a.output/'all-capture-events.json',[dict(event=q,raw_slice_sha256=digest(data(q['wall'])))for q in caps]);rom=b['raw'];font=cfg['diagnostic']['CHR_offset'];glyphs=[]
 def glyph(page,t):
  v=rom[font+page*1024+t*16:font+page*1024+t*16+16];return[((v[y]>>(7-x))&1)|(((v[y+8]>>(7-x))&1)<<1)for y in range(8)for x in range(8)]
 def classes(im,page,tiles,xy):
  m=collections.defaultdict(set)
  for t,(x,y)in zip(tiles,xy):
   for k,v in zip(glyph(page,t),im.crop((x,y,x+8,y+8)).getdata()):m[k].add(v)
  assert all(len(v)==1 for v in m.values());v={k:next(iter(x))for k,x in m.items()};assert len(v)==len(set(v.values()));return v
 selected=[]
 for case,c in enumerate(cfg['cases'],1):
  cs=[q for q in caps if q['data']['name'].startswith(c['name']+'-')];hud=next(q for q in cs if q['data']['name']==c['name']+'-selected-HUD');im=image(hud['wall']);names=classes(im,c['icon_bank'],c['hud_name'],[(24+i*8,8)for i in range(7)]);icons=classes(im,c['icon_bank'],[42,43,44,45],[(184,8),(192,8),(184,16),(192,16)]);assert icons[0]==names[0]and icons[1]==names[1];glyphs.append(dict(case=case,name=c['name'],ordinal=hud['wall'],name_classes=names,icon_classes=icons,page=c['icon_bank']))
  chosen=[next(q for q in cs if q['data']['name']==c['name']+'-'+s)for s in['selected-HUD','funded-setup','contact','natural-cleanup','exhaust-refusal','selection-cleanup']]
  chosen +=[q for q in cs if '-art-'in q['data']['name']]
  chosen.append(next(q for q in cs if q['data']['name']==c['name']+'-actual-debit-zero'));chosen.append(next(q for q in cs if q['data']['name'].endswith('-pool-setup')))
  for q in chosen:selected.append(dict(case=case,item=c['item'],label=q['data']['name'],ordinal=q['wall'],epoch=rows[q['wall']-1],raw_sha256=digest(data(q['wall']))))
 put(a.output/'HUD-source-pixel-classes.json',dict(passed=True,rows=glyphs,scope='All14actual selected name/icon patterns vs immutable source2bpp and distinct consistent RGB classes. Not an independent palette reconstruction or effect/allbackground pixel verdict.'))
 sheets=[]
 for item in range(1,8):
  entries=[q for q in selected if q['item']==item]
  for part,start in enumerate(range(0,len(entries),20),1):
   chosen=entries[start:start+20];im=Image.new('RGB',(4*272,5*272),(28,28,28));draw=ImageDraw.Draw(im);placements=[]
   for k,q in enumerate(chosen):
    x=k%4*272;y=k//4*272;im.paste(image(q['ordinal']),(x,y+30));draw.text((x+1,y+1),f'PPU{q["epoch"]["ppu_frame"]} / u{q["epoch"]["updates"]}',fill='white');draw.text((x+1,y+14),q['label'][:35],fill='white');placements.append(dict(x=x,y=y+30,width=256,height=240,frame=q))
   path=a.output/f'item-{item:02}-whole-PPU-{part:02}.png';im.save(path);sheets.append(dict(image=bind(path),placements=placements))
 put(a.output/'selection.json',selected);put(a.output/'sheets.json',sheets)
 apu=list(csv.DictReader((n/'apu.csv').open(newline='')));actual=[q for q in apu if int(q['register'])<=0x4013 or int(q['register'])==0x4015];put(a.output/'APU-scope.json',dict(actual_APU_bus_writes=len(actual),DMA_controller_records=len(apu)-len(actual),case_APU_counts=dict(collections.Counter(q['case']for q in actual)),individual_source_cue_and_waveform_fidelity_proven=False,scope='APU activity includes mixed music/SFX. Exact per-weapon request identity/reference waveform not instrumented.'))
 prior=D/'current0a-mega-common-observed-v1';oldledger=json.loads((prior/'actual-case-ledger.json').read_text())['rows'];historical=[]
 for old,current in zip(oldledger,ledger):
  assert old['name']==current['name']and old['funded_seed']==current['funded_seed']and old['native_paid']==current['native_paid']
  historical.append(dict(name=current['name'],same_seed_and_paid=True,historical_native_credit=old['native_credit'],current_native_credit=current['native_credit'],historical_end=old['funded_end'],current_end=current['funded_end']))
 put(a.output/'historical0a-comparison.json',dict(passed=True,historical_0a_proof=bind(D/'current0a-mega-common-final-v1/proof.json'),rows=historical,scope='Same14 controlled plans and measured source-paid costs. Different ROM/render/audio/palette/runtime epochs; no all-input/pixel/cadence identity or causal speedup claim. Historical FALSEs/hashes remain unchanged.'))
 facts=dict(passed=True,native_execution_passed=True,original_collector_passed=np['passed'],original_collector_proof_sha256=sha(n/'proof.json'),ROM_sha256=SHA,actual_mode=1,variant=0,controlled_cases=14,acquisition=False,ready_bindings=verified,complete_PPU_frames=len(rows),raw_bytes=(n/'actual-ppu.argb').stat().st_size,raw_sha256=sha(n/'actual-ppu.argb'),complete256_DMA=len(hashes),literal_byte_equal_DMA=literal,ignored_attribute_DMA=ignored_DMAs,ignored_attribute_bytes=ignored_bytes,implemented_differences=0,source_publication_match_DMA=matched,startFrames=counters['startFrame-hardware'],pending_starts=counters['pending_starts'],safe_enables=counters['safe_enables'],actual_endFrame_publication_checks=z['complete_dma_checks'],native_updates=z['updates'],native_nmis=z['nmis'],minSP=z['minSP'],actual_IRQ31=z['irq_scroll_stores'],hardware_CHR_checks=z['hardware_chr_checks'],captures=len(caps),unique_capture_files=len(lastcaps),selected_wholeframes=len(selected),sheets=len(sheets),terminal_emptyChecked=[q['emptyChecked']for q in z['cases']],actual_refusals_independently_witnessed=14,native_worker_released=True,agent_visual_review=False,limits=['B-only inventory/resources/complete arena/target seeds, not acquisition.','Current collector retains raw false transient flags and requires real orderedcasewitnesses; historical0a FALSEs remainunchanged.','Actual pattern/CHR owner and selected HUD source pixel classes, not every visible effect/body/background pixel.','Tiny HUD/ordinary hardware sprite visibility/clip/rotation/source art/campaign/allitems/FPS/globalNMIworstcase/waveform fidelity remain open.'])
 put(a.output/'facts.json',facts);refs={Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',a.ready/'ROOT-grant.json'}|{q for q in n.iterdir()if q.is_file()}|{q for q in a.output.iterdir()if q.is_file()};put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(refs,key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,independent_actual_scope=True,native_execution_passed=True,original_collector_passed=np['passed'],agent_visual_review=False,ROM_sha256=SHA,native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(refs),native_worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),facts=facts),indent=2))
if __name__=='__main__':main()
