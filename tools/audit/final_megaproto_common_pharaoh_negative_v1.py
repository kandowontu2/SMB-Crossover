"""Freeze exact0a E3-gallery Lua-name collision; no native retry or game edit."""
from pathlib import Path
import argparse, collections, csv, hashlib, json
from PIL import Image, ImageDraw
from final_megaproto_common_source_v2 import D, R, SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def bind(p):return dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))
def encoded(s):return[v&0xe3 if i%4==2 else v for i,v in enumerate(s)]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current0a-mega-common-oam-ready-v2';assert verify_manifest(ready/'manifest.json')==967;n=ready/'native';prior=D/'current0a-mega-common-ready-v5/native';proof=json.loads((n/'proof.json').read_text());cfg=json.loads((n/'config.json').read_text());assert proof['passed']is False and proof['runner_exit']==1 and proof['dependencies_unchanged']and proof['native_worker_released']and proof['ROM_sha256']==SHA
 for name,b in proof['bindings'].items():assert(n/name).stat().st_size==b['bytes']and sha(n/name)==b['sha256']
 assert not(n/'first-failure.json').exists()and not(n/'native-megaproto-common.json').exists()and not(n/'ppu-capture-native-result.json').exists()
 text=(n/'run.lua').read_text();cause="attempt to call a table value (local 'owner')";assert cause in(n/'candidate-run.log').read_text()and 'run.lua:395' in(n/'candidate-run.log').read_text();ls=text.splitlines();assert ls[393].strip().startswith('local owner=current;')and "owner())==4"in ls[394]and 'local function owner()return C.identity.owner end'in text
 events=[json.loads(s)for s in(n/'events.jsonl').open()];old_events=[json.loads(s)for s in(prior/'events.jsonl').open()];assert events[:len(old_events)]==old_events
 old_size=(prior/'actual-ppu.argb').stat().st_size
 with(n/'actual-ppu.argb').open('rb')as f:prefix=f.read(old_size)
 assert digest(prefix)==sha(prior/'actual-ppu.argb')
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));old_rows=list(csv.DictReader((prior/'actual-ppu-index.csv').open(newline='')));assert rows[:len(old_rows)]==old_rows;assert len(rows)==2355 and(n/'actual-ppu.argb').stat().st_size==len(rows)*245760
 assert all(int(z['mode'])==1 for z in rows if int(z['updates'])>0)
 counts=collections.Counter();last=None;raw_D=[];literal=ignored_DMAs=ignored_bytes=matched=0;hashes=[]
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line);counts[q['kind']]+=1
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==len(hashes)+1 and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['hardware']==encoded(q['source'])and not q['implemented_differences']
   assert q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   assert all(w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0 for i,w in enumerate(q['writes']))
   diff=[dict(offset=i,source=x,hardware=y)for i,(x,y)in enumerate(zip(q['source'],q['hardware']))if x!=y];assert diff==list(q['differences'])==list(q['ignored_attribute_differences']);literal+=not diff;ignored_DMAs+=bool(diff);ignored_bytes+=len(diff);matched+=q['source_publication_match'];last=q
   hashes.append(dict(id=q['id'],source_sha256=digest(bytes(q['source'])),physical_sha256=digest(bytes(q['hardware'])),ignored_attribute_differences=diff))
  elif q['kind']=='startFrame-hardware'and q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['completed_dma_id']==last['id']and q['hardware']==last['hardware']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:assert q['safe'];counts['safe_scoped_enables']+=1
  if len(raw_D)<1590:
   z=dict(q);z.pop('implemented_differences',None);z.pop('ignored_attribute_differences',None);raw_D.append(z)
 original_D=[json.loads(s)for s in(prior/'ability-dma-epochs.jsonl').open()];assert len(original_D)==1590 and raw_D==original_D
 assert len(hashes)==2201 and literal==1886 and ignored_DMAs==315 and ignored_bytes==392 and counts['safe_scoped_enables']==1873 and counts['startFrame-hardware']==2355
 put(a.output/'all-DMA-hashes.json',hashes);put(a.output/'old-prefix-equivalence.json',dict(passed=True,complete_PPU_frames=len(old_rows),raw_bytes=old_size,raw_sha256=digest(prefix),all_events=len(old_events),all_raw_DMA_timing_rows=len(original_D),normalization='Only the two additive classification arrays removed from new rows; all old fields/values exact.',original392_FALSE_unchanged=True))
 caps=[q for q in events if q['kind']=='ppu-frame-captured'];raw=(n/'actual-ppu.argb').open('rb')
 def data(i):raw.seek((i-1)*245760);b=raw.read(245760);assert len(b)==245760;return b
 def image(i):return Image.frombytes('RGBA',(256,240),data(i),'raw','BGRA').convert('RGB')
 last_caps={q['data']['name']:q for q in caps}
 for name,q in last_caps.items():assert(n/(name+'.argb')).read_bytes()==data(q['wall'])
 put(a.output/'all-capture-events.json',[dict(event=q,raw_sha256=digest(data(q['wall'])))for q in caps])
 ledgers=[];selection=[]
 for case,c in enumerate(cfg['cases'][:6],1):
  es=[q for q in events if q['case']==case];phases=[q for q in es if q['kind']=='gallery-phase'];funded=[q for q in es if q['phase']=='funded'];spends=[q for q in funded if q['kind']=='actual-source-spend'];contacts=[q for q in funded if q['kind']=='actual-source-contact'];zeros=[q for q in funded if q['kind']=='actual-funded-debit-zero'];credits=[q for q in funded if q['kind']=='actual-funded-refill-credit'];assert len(contacts)==1 and len(zeros)==1 and not credits
  paid=sum(q['data']['cost']for q in spends if q['data']['accepted']);assert paid==c['initial_stock']and zeros[0]['data']['after']==0
  empty=next(q for q in phases if q['phase']=='empty');end_empty=next(q for q in phases if q['phase']=='setup-pool');assert end_empty['update']-empty['update']==25
  for q in[empty,end_empty]:assert q['data']['ammo']==0 and q['data']['held']==0 and q['data']['kick']!=1 and all(s['type']==0 for s in q['data']['shots'])
  assert not[q for q in es if q['phase']=='empty'and q['kind']=='actual-special-spawn'];assert not[q for q in es if q['phase']=='empty'and q['kind']=='actual-source-spend'and q['data']['accepted']]
  cleanup=next(q for q in events if q['case']==case+1 and q['kind']=='gallery-phase'and q['phase']=='next');assert cleanup['data']['held']==0 and all(s['type']==0 for s in cleanup['data']['shots'])
  cs=[q for q in caps if q['data']['name'].startswith(c['name']+'-')]
  for suffix in['selected-HUD','contact','natural-cleanup','exhaust-refusal','selection-cleanup']:
   assert any(q['data']['name']==c['name']+'-'+suffix for q in cs)
  pool=[q for q in es if q['kind']in['actual-full-pool-refusal','actual-full-pool-special']];assert len(pool)==1
  ledgers.append(dict(case=case,name=c['name'],source_spends=spends,contacts=contacts,actual_zero=zeros[0],empty_entry=empty,empty_exit=end_empty,pool=pool[0],selection_cleanup=cleanup,scope='Completed six case assertion paths only; aggregate remains FALSE. Refusal has actual zero stock/no spawn/no accepted debit plus25-update phase and postassert capture, not terminal presence alone.'))
  wanted=[next(q for q in cs if q['data']['name']==c['name']+'-'+s)for s in['selected-HUD','contact','natural-cleanup','exhaust-refusal','selection-cleanup']]
  wanted.insert(1,next(q for q in cs if q['data']['name']==c['name']+'-art-'+str(c['contact_type'])))
  wanted.append(next(q for q in cs if q['data']['name'].endswith('-pool-setup')))
  for q in wanted:selection.append(dict(case=case,label=q['data']['name'],ordinal=q['wall'],epoch=rows[q['wall']-1],raw_sha256=digest(data(q['wall']))))
 put(a.output/'six-case-witnesses.json',dict(passed=True,native_aggregate_remains_FALSE=True,complete_case_paths=6,rows=ledgers))
 # The seventh case stops inside the observer BEFORE the direct-release leaf.
 case7=[q for q in caps if q['data']['name'].startswith('pharaoh-face1-')]
 for suffix in['selected-HUD','funded-setup','art-12','art-18']:
  q=next(q for q in case7 if q['data']['name']=='pharaoh-face1-'+suffix);selection.append(dict(case=7,label=q['data']['name'],ordinal=q['wall'],epoch=rows[q['wall']-1],raw_sha256=digest(data(q['wall']))))
 for ordinal in[2353,2354,2355]:selection.append(dict(case=7,label='last-complete-before-observer-error',ordinal=ordinal,epoch=rows[ordinal-1],raw_sha256=digest(data(ordinal))))
 # Pixel classes for the seven actual selected names/icons against source CHR.
 rom=(n/'candidate.nes').read_bytes();font=cfg['diagnostic']['CHR_offset'];glyphs=[]
 def glyph(page,t):
  z=rom[font+page*1024+t*16:font+page*1024+t*16+16];return[((z[y]>>(7-x))&1)|(((z[y+8]>>(7-x))&1)<<1)for y in range(8)for x in range(8)]
 def classes(im,page,tiles,xy):
  m=collections.defaultdict(set)
  for t,(x,y)in zip(tiles,xy):
   for k,v in zip(glyph(page,t),im.crop((x,y,x+8,y+8)).getdata()):m[k].add(v)
  assert all(len(v)==1 for v in m.values());z={k:next(iter(v))for k,v in m.items()};assert len(z)==len(set(z.values()));return z
 for c in cfg['cases'][:7]:
  q=next(q for q in caps if q['data']['name']==c['name']+'-selected-HUD');im=image(q['wall']);names=classes(im,c['icon_bank'],c['hud_name'],[(24+i*8,8)for i in range(7)]);icons=classes(im,c['icon_bank'],[42,43,44,45],[(184,8),(192,8),(184,16),(192,16)]);assert icons[0]==names[0]and icons[1]==names[1];glyphs.append(dict(name=c['name'],ordinal=q['wall'],page=c['icon_bank'],name_classes=names,icon_classes=icons))
 put(a.output/'selected-HUD-pixel-classes.json',dict(passed=True,source_2bpp_class_checks=glyphs,scope='Actual seven selected names/icons vs immutable source patterns. Not independent palette reconstruction/all-HUD/effect pixels.'))
 sheets=[]
 for start in range(0,len(selection),14):
  chosen=selection[start:start+14];sheet=Image.new('RGB',(4*272,4*272),(28,28,28));draw=ImageDraw.Draw(sheet);placements=[]
  for k,q in enumerate(chosen):
   x=k%4*272;y=k//4*272;sheet.paste(image(q['ordinal']),(x,y+30));draw.text((x+1,y+1),f'PPU{q["epoch"]["ppu_frame"]} / u{q["epoch"]["updates"]}',fill='white');draw.text((x+1,y+14),q['label'][:35],fill='white');placements.append(dict(x=x,y=y+30,width=256,height=240,frame=q))
  path=a.output/f'whole-PPU-{start//14+1:02}.png';sheet.save(path);sheets.append(dict(image=bind(path),placements=placements))
 put(a.output/'selection.json',selection);put(a.output/'sheets.json',sheets)
 apu=list(csv.DictReader((n/'apu.csv').open(newline='')));actual=[q for q in apu if int(q['register'])<=0x4013 or int(q['register'])==0x4015];put(a.output/'APU-scope.json',dict(actual_APU_writes=len(actual),DMA_controller_records=len(apu)-len(actual),case_counts=dict(collections.Counter(q['case']for q in actual)),scope='Actual APU bus activity includes music/mixed SFX. No per-weapon request hook or reference waveform comparison; no individual sound identity claim.'))
 facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,actual_numeric_mode=1,variant=0,failure_kind='Lua observer runtime name shadowing, not native game/PPU assertion',literal_failure=cause,source_line=395,first_failure_json_absent=True,completed_cases=6,current_case=7,current_phase='funded',last_complete_PPU=2355,last_complete_update=1956,complete256_DMA=2201,literal_byte_equal_DMA=1886,ignored_attribute_DMA=315,ignored_attribute_bytes=392,implemented_differences=0,safe_enables=1873,startFrames=2355,source_publication_matched_DMA=matched,complete_raw_bytes=(n/'actual-ppu.argb').stat().st_size,all_case_captures=len(caps),unique_capture_names=len(last_caps),selected_whole_frames=len(selection),native_worker_released=True,no_retry=True,game_changes=False,agent_visual_review=False,classification='Helper owner() introduced by typed Mega adaptation is shadowed by preexisting local owner=current at real ReleaseBalloon hook. Source/mock coverage missed this runtime closure. Actual direct-release debit/remaining cases are unobserved, not inferred from source.',missing=['PHARAOH full release/cost/contact/cleanup','KICK/FLAME/WATER cases','terminal native mechanics/fullPPU components'],source_context=ls[380:404],no_error_state_backfill='No native error PC/SP snapshot exists; hook entry metadata is compiled source, not a logged fault state.')
 put(a.output/'facts.json',facts)
 refs={Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant.json',prior/'proof.json'}|{q for q in n.iterdir()if q.is_file()}|{q for q in a.output.iterdir()if q.is_file()};put(a.output/'manifest.json',dict(bindings=[bind(q)for q in sorted(refs,key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,ROM_sha256=SHA,native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(refs),agent_visual_review=False,native_worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),facts=facts),indent=2))
if __name__=='__main__':main()
