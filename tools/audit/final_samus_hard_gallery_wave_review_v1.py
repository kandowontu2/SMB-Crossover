"""Independent literal-result/raw DMA/case-image review preparation; no native run."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current3b112-samus-hard-wave-ready-v1';assert verify_manifest(ready/'manifest.json')==1049;n=ready/'native';native=json.loads((n/'proof.json').read_text());fail=json.loads((n/'first-failure.json').read_text());assert not native['passed'] and native['runner_exit']==1 and native['dependencies_unchanged'] and fail['message']=='Native IRQ/CHR/DMA exercised'
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];done=[q for q in events if q['kind']=='samus-subphase-complete'];cfg=json.loads((n/'config.json').read_text());expected=[(q['case'],t['kind'],t['face'])for q in cfg['cases']for t in q['tasks']];assert[(q['case'],q['data']['task']['kind'],q['data']['task']['face'])for q in done]==expected and len(done)==27
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert len(rows)==2718 and(n/'actual-ppu.argb').stat().st_size==2718*245760 and all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
 raw=(n/'actual-ppu.argb').open('rb')
 def frame(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 previous=D/'current3b112-samus-hard-freeze-clock-ready-v1/native';prefix=0;h=hashlib.sha256()
 with(previous/'actual-ppu.argb').open('rb')as f:
  for i in range(1,1904):
   z=frame(i)
   if f.read(245760)!=z:break
   prefix+=1;h.update(z)
 assert prefix==1897
 caps=[q for q in events if q['kind']=='ppu-frame-captured'];last={q['data']['name']:q for q in caps};saved=[]
 for name,q in last.items():
  file=n/(name+'.argb');assert file.read_bytes()==frame(q['wall']);saved.append(dict(name=name,path=str(file),sha256=sha(file),actual_ordinal=q['wall'],source_request_wall=q['data']['wall'],actual_PPU=rows[q['wall']-1]))
 assert len(caps)==193 and len(saved)==192
 completed=starts=enables=matches=0;lastDMA=None
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   completed+=1;matches+=bool(q['source_publication_match']);assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware'] and not q['differences'];assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i] and w['stamp']['mask']&24==0
   lastDMA=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==lastDMA['source'] and q['completed_dma_id']==lastDMA['id']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:enables+=1;assert q['safe']
 assert(completed,starts,enables,matches)==(2671,2717,2354,0)
 selected=collections.defaultdict(dict)
 for q in caps:selected[min(q['case'],8)].setdefault(q['wall'],[]).append(q['data']['name'])
 # Observe subsequent actual visible epochs around effect/contact/hurt, not just
 # the publication-delayed source request. Every original capture stays listed.
 for q in events:
  if q['kind']in['actual-Samus-contact','actual-bomb-boost','actual-intended-injury','actual-Ice-thaw','actual-Ice-break']:
   for delta in[-1,2]:
    i=q['wall']+delta
    if 1<=i<=len(rows):selected[min(q['case'],8)].setdefault(i,[]).append(q['kind']+f' {delta:+d} actual PPU')
 sheets=[];placements=[]
 for case in range(1,9):
  chosen=sorted(selected[case].items())
  for page,start in enumerate(range(0,len(chosen),16),1):
   part=chosen[start:start+16];im=Image.new('RGB',(4*272,((len(part)+3)//4)*280),(32,32,32));draw=ImageDraw.Draw(im)
   for k,(i,names)in enumerate(part):
    z=frame(i);x=k%4*272;y=k//4*280;im.paste(Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB'),(x,y+32));draw.text((x+2,y+1),f'Actual PPU{rows[i-1]["ppu_frame"]}/ordinal{i}',fill='white');draw.text((x+2,y+15),' / '.join(names)[:43],fill='white');placements.append(dict(case=case,sheet=f'case{case}-page{page}.png',ordinal=i,names=names,x=x,y=y+32,width=256,height=240,actual_PPU=rows[i-1],raw_slice_sha256=hashlib.sha256(z).hexdigest()))
   file=a.output/f'case{case}-page{page}.png';im.save(file);sheets.append(dict(path=str(file),sha256=sha(file),placements=len(part)))
 Image.frombytes('RGBA',(256,240),(n/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB').save(a.output/'first-failure-partial.png')
 put(a.output/'selection.json',placements);put(a.output/'case-captures.json',dict(capture_events=193,last_named_files=192,overwritten_name='Long-beyond-short-range',saved=saved))
 put(a.output/'mechanical-chronology.json',dict(completed=done,important=[q for q in events if q['kind']in['actual-missile-debit','actual-full-freeze-clock-boundary','actual-Ice-thaw','actual-Ice-break','actual-wave-page-cross','actual-intended-injury','controlled-single-contact-hazard-retired']]))
 facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,mode=1,lane='B controlled native-engine use, not acquisition',actual_completed_subphase_assertions=27,actual_case_plan=cfg['cases'],terminal_failure=fail,full_actual_PPU_frames=2718,complete256DMAs=completed,startFrames=starts,safe_scoped_enables=enables,source_publication_matches=matches,unchanged_PPU_prefix=prefix,prefix_raw_sha256=h.hexdigest(),all_saved_capture_bytes_match_raw=True,capture_events=193,saved_files=192,selected_wholeframe_placements=len(placements),sheets=sheets,missing_observer_scope='Shared RosterOamReady is rotated-tail only. Samus selected2 uses legacy/nonrotated completion, so published remainsnil, legacy dmaChecks stays0, source-publication/bodyDisplayed-CHR chain is unexercised. Global mapper latch checks and strict E008 hardware protocol are separate. No missing per-case result JSON is invented.',worker_released=True)
 put(a.output/'facts.json',facts)
 refs=[Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant.json',D/'current3b112-samus-hard-terminal-owner-v2/proof.json',D/'current3b112-samus-hard-wave-negative-v1/proof.json'];refs+=list(q for q in n.iterdir()if q.is_file());refs+=list(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(set(refs),key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,interpretation_only=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),placements=len(placements),sheets=sheets),indent=2))
if __name__=='__main__':main()
