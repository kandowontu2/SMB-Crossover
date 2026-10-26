"""Independent successful native/raw publication/DMA and actual-frame review input."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=D/'current3b112-samus-hard-publication-ready-v2';assert verify_manifest(ready/'manifest.json')==1079;n=ready/'native';native=json.loads((n/'proof.json').read_text());assert native['passed']and native['runner_exit']==0 and native['dependencies_unchanged']and not(n/'first-failure.json').exists();result=json.loads((n/'native-samus-gallery.json').read_text());assert result['passed']and result['actual_mode_readback']==1 and not result['acquisition']and len(result['cases'])==8
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];pubs=[q for q in events if q['kind']=='actual-Samus-complete-publication'];other=[q for q in events if q['kind']!='actual-Samus-complete-publication'];old=D/'current3b112-samus-hard-wave-ready-v1/native';prior=[json.loads(s)for s in(old/'events.jsonl').read_text().splitlines()];assert other==prior
 assert len(pubs)==2259 and[q['data']['id']for q in pubs]==list(range(1,2260));catalog=collections.defaultdict(list)
 for q in pubs:
  z=q['data'];assert len(z['source'])==256 and q['pc']==z['returnPC']==366 and q['sp']==z['returnSP']==245 and q['bank']==z['returnBank']==0 and q['update']==z['update']
  body=z.get('body')
  if body:assert body['update']==q['update'] and body['bank']==13 and body['physical']>=0
  catalog[bytes(z['source'])].append(q)
 assert sum(bool(q['data'].get('body'))for q in pubs)==2199 and sum(q['data']['postFinish']for q in pubs)==388
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));oldrows=list(csv.DictReader((old/'actual-ppu-index.csv').open(newline='')));assert rows==oldrows and len(rows)==2718 and(n/'actual-ppu.argb').stat().st_size==2718*245760
 h=hashlib.sha256()
 with(n/'actual-ppu.argb').open('rb')as f,(old/'actual-ppu.argb').open('rb')as g:
  while z:=f.read(245760):assert z==g.read(245760);h.update(z)
 assert h.hexdigest()==sha(old/'actual-ppu.argb')
 completed=starts=enables=matches=0;last=None;chain=[];guard_eligible=0;no_body=0;ambiguous=0
 with(old/'ability-dma-epochs.jsonl').open()as f:
  for line in(n/'ability-dma-epochs.jsonl').open():
   q=json.loads(line);priorrow=json.loads(next(f));normalize=dict(q);normalize.pop('source_publication_match',None);priorrow.pop('source_publication_match',None);assert normalize==priorrow
   if q['kind']=='completed-DMA-before-render-enable':
    completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware'] and not q['differences'];assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
    for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i] and w['stamp']['mask']&24==0
    if q['source_publication_match']:
     matches+=1;candidates=catalog[bytes(q['source'])];assert candidates;physical={(z['data'].get('body')or{}).get('physical')for z in candidates};ambiguous+=len(physical)>1
     chain.append(dict(DMA_id=q['id'],start=q['start'],complete=q['complete'],actual_current_source_publication_match=True,matching_whole_run_catalogue_ids=[z['data']['id']for z in candidates],catalogue_physical_pages=sorted(x for x in physical if x is not None),catalogue_can_include_hidden_body=None in physical,warning='Catalogue IDs are not a unique temporal ID. Actual live bodyDma is bound by the unchanged4014 callback to the latest published body only when full256source equality succeeds; startFrame checks actual mapper.chrBanks0. Raw per-frame mapper value was not separately dumped.'))
    last=q
   elif q['kind']=='startFrame-hardware':
    starts+=1;assert len(q['hardware'])==256
    if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==last['source'] and q['completed_dma_id']==last['id']
   elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:enables+=1;assert q['safe']
  assert not f.read()
 assert(completed,starts,enables,matches)==(2671,2717,2354,2319)and result['complete_dma_checks']==2318
 put(a.output/'publication-DMA-chain.json',dict(passed=True,published256=2259,body_present_publications=2199,legitimate_no_body_publications=60,post_Finish_publications=388,source_matched_actual_DMAs=2319,endFrame_publication_checks=2318,full_body_physical_assertion='Original actual startFrame mapper.chrBanks0 assertion retained and executed whenever the live matched bodyDma is nonnil. Fixed callback source/state chain is source/model qualified. Offline raw log independently proves full256source/hardware and current source publication flag; per-startFrame physical mapper operands were not separately serialized.',catalogue_global_physical_ambiguities=ambiguous,rows=chain,scope='No cycle-unique publicationID invented from wall labels or OAM signatures. The same OAM bytes can legitimately belong to different CHR pages in different poses/periods.'))
 caps=[q for q in events if q['kind']=='ppu-frame-captured'];lastcap={q['data']['name']:q for q in caps};raw=(n/'actual-ppu.argb').open('rb')
 def frame(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 for name,q in lastcap.items():assert(n/(name+'.argb')).read_bytes()==frame(q['wall'])
 oldreview=D/'current3b112-samus-hard-wave-observed-v1';selected=json.loads((oldreview/'selection.json').read_text());assert len(selected)==151;sheets=[]
 for name in dict.fromkeys(q['sheet']for q in selected):
  part=[q for q in selected if q['sheet']==name];im=Image.new('RGB',(4*272,((len(part)+3)//4)*280),(32,32,32));draw=ImageDraw.Draw(im)
  for q in part:
   z=frame(q['ordinal']);assert hashlib.sha256(z).hexdigest()==q['raw_slice_sha256'];im.paste(Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB'),(q['x'],q['y']));draw.text((q['x']+2,q['y']-31),f'Actual PPU{rows[q["ordinal"]-1]["ppu_frame"]}/ordinal{q["ordinal"]}',fill='white');draw.text((q['x']+2,q['y']-17),' / '.join(q['names'])[:43],fill='white')
  file=a.output/name;im.save(file);assert file.read_bytes()==(oldreview/name).read_bytes();sheets.append(dict(path=str(file),sha256=sha(file),placements=len(part)))
 put(a.output/'selection.json',selected);facts=dict(passed=True,ROM_sha256=SHA,mode=1,lane='B controlled native use; not acquisition',mechanical_cases=8,subphases=27,actual_updates=result['updates'],actual_nmis=result['nmis'],actual_IRQ31_store_checks=result['irq_scroll_stores'],actual_hardwareCHR_latch_checks=result['hardware_chr_checks'],minSP=result['minSP'],APU_register_DMA_controller_writes=result['apuWrites_includingDMAController'],fullPPUframes=2718,fullPPUbytes=2718*245760,raw_sha256=h.hexdigest(),complete256DMAs=completed,startFrames=starts,safe_scoped_enables=enables,source_matched_DMA=matches,publications=2259,body_present_publications=2199,post_Finish_publications=388,original_false_run_all_raw_PPU_identical=True,original_source_events_semantically_identical_except_new_publications=True,all_DMA_timing_and_bytes_identical_except_fixed_source_publication_flag=True,capture_events=len(caps),last_named_files=len(lastcap),all_saved_capture_files_match_raw=True,selected_actual_wholeframes=151,sheets=sheets,actual_case_results=result['cases'],worker_released=True)
 put(a.output/'facts.json',facts);refs=[Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant.json',old/'proof.json',old/'ability-dma-epochs.jsonl',old/'actual-ppu.argb',old/'actual-ppu-index.csv',old/'events.jsonl',oldreview/'proof.json',oldreview/'selection.json'];refs+=list(q for q in n.iterdir()if q.is_file());refs+=list(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(set(refs),key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,native_mechanical_pass=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),worker_released=True,limits='Independent mechanical/raw publication/hardware checks. Whole-frame agent review remains separate; not acquisition, waveform, global timing or everypixel fidelity.'));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),sheets=sheets),indent=2))
if __name__=='__main__':main()
