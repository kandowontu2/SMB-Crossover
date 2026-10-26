"""Read-only preservation/review material for the first BassEasy deadline FALSE."""
from pathlib import Path
import argparse,collections,csv,hashlib,json,sys
from PIL import Image,ImageDraw
from final_inventory_bass731_run_v1 import verify_manifest,ROOT,SHA
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda b:hashlib.sha256(b).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==SHA;bindings=verify_manifest(a.ready/'manifest.json')
 out=Path(next(q for q in ready['profiles']if q['profile']=='bass-easy')['output']);hard=Path(next(q for q in ready['profiles']if q['profile']=='bass-hard')['output']);assert not(hard/'launch.json').exists()
 original=json.loads((out/'proof.json').read_text());assert original['passed']is False and original['runner_exit']==1
 failure=json.loads((out/'first-failure.json').read_text());assert failure['message']=='Scoped render enable precedes native pre-render vertical reload'
 frames=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')));size=(out/'actual-ppu.argb').stat().st_size;assert size==len(frames)*245760
 assert [int(q['ordinal'])for q in frames]==list(range(1,len(frames)+1))
 events=[json.loads(s)for s in(out/'events.jsonl').read_text().splitlines()];caps=[q for q in events if q['kind']=='ppu-frame-captured'];lastcaps={q['data']['name']:q for q in caps}
 phases=[q for q in events if q['kind']=='gallery-phase'];source=[q for q in events if q['kind']in['actual-source-effect-draw','actual-special-spawn','actual-source-contact','actual-source-spend','actual-water-effect-emitter','actual-full-pool-special','actual-buster-full-pool-refusal','actual-controller-selection','controlled-falling-Goomba-target']]
 put(a.output/'source-events.json',source);put(a.output/'phase-history.json',phases)
 completed=starts=pending=enables=0;unsafe=[];last=None;last_starts=[];complete_hashes=[]
 for line in(out/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   assert q['id']==completed+1 and len(q['source'])==len(q['hardware'])==256 and q['source']==q['hardware']and not q['differences']
   assert len(q['writes'])==256 and q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008
   assert q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['value']==q['source'][i]and w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0
   completed+=1;last=q;complete_hashes.append(dict(id=q['id'],source_sha256=digest(bytes(q['source'])),hardware_sha256=digest(bytes(q['hardware']))))
  elif q['kind']=='startFrame-hardware':
   starts+=1;pending+=bool(q.get('pending_dma_id'));assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert last['id']==q['completed_dma_id']and last['source']==q['hardware']
   last_starts=(last_starts+[q])[-3:]
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   enables+=1;s=q['stamp'];safe=241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274
   assert safe==q['safe']
   if not safe:unsafe.append(q)
 assert len(unsafe)==1 and unsafe[0]['stamp']==dict(bankA=0,pc=0xe00b,cycle=20,cpu=38923130,oamaddr=0,scanline=0,frame=1308,mask=30,sp=244,bankC=116)
 put(a.output/'all-completed-DMA-hashes.json',complete_hashes)
 put(a.output/'first-late-enable.json',dict(failure=failure,unsafe_enable=unsafe[0],immediately_preceding_DMA=last,last3startFrame=last_starts,earliest_scoped_late_enable=True,physical_corruption=False,queue_payload_captured=False,limits='No actual VRAM packet/parser/NMI-entry trace was captured. Timestamp proves missed safe vertical-reload window; first-failure image is mid-frame0, not a completed failing whole frame. No invented packet/cost attribution.'))
 raw=(out/'actual-ppu.argb').open('rb');derived=[]
 def frame(ordinal,label,reason):
  q=frames[ordinal-1];raw.seek((ordinal-1)*245760);data=raw.read(245760);assert len(data)==245760
  f=a.output/'frames'/(label+'.png');f.parent.mkdir(exist_ok=True);im=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB');im.save(f)
  row=dict(path=str(f),sha256=sha(f),raw_slice_sha256=digest(data),ordinal=ordinal,actual_PPU=q,reason=reason);derived.append(row);return row
 for i,q in enumerate(caps,1):frame(q['wall'],f'{i:03}-{q["data"]["name"]}',dict(kind='exact original case capture event',source_event=q))
 for ordinal in range(max(1,len(frames)-12),len(frames)+1):frame(ordinal,f'context-{ordinal:06}',dict(kind='last completed actual PPU context before stopped failing frame'))
 for name,q in lastcaps.items():
  raw.seek((q['wall']-1)*245760);assert(out/(name+'.argb')).read_bytes()==raw.read(245760)
 put(a.output/'frame-selection.json',derived)
 sheets=[]
 for start in range(0,len(derived),9):
  entries=derived[start:start+9];im=Image.new('RGB',(3*272,3*280),(32,32,32));draw=ImageDraw.Draw(im);placements=[]
  for i,q in enumerate(entries):
   x=i%3*272;y=i//3*280;im.paste(Image.open(q['path']),(x,y+32));draw.text((x+2,y+1),f'{start+i+1}: PPU {q["actual_PPU"]["ppu_frame"]} / ordinal{q["ordinal"]}',fill='white');draw.text((x+2,y+15),Path(q['path']).stem[:38],fill='white');placements.append(dict(x=x,y=y+32,width=256,height=240,frame=q))
  f=a.output/f'whole-PPU-sheet-{len(sheets)+1:02}.png';im.save(f);sheets.append(dict(path=str(f),sha256=sha(f),placements=placements))
 put(a.output/'sheets.json',sheets)
 observed=collections.defaultdict(collections.Counter)
 for q in events:observed[q['case']][q['kind']]+=1
 z=dict(preserved_original_FALSE=True,passed=False,source_integrity_passed=True,native_run=False,ROM_sha256=SHA,original_native_proof=str(out/'proof.json'),original_native_proof_sha256=sha(out/'proof.json'),ready_sha256=sha(a.ready/'proof.json'),ready_bindings_verified=bindings,actual_numeric_mode=0,Hard_launched=False,complete_profile=False,planned_cases=16,observed_case_indices=sorted(observed),prior_component_prefix_cases=[1,2,3],event_counts={k:dict(v)for k,v in observed.items()},complete256DMAs=completed,actual_data_writes=completed*256,startFrame_snapshots=starts,pending_startFrames=pending,scoped_enables=enables,safe_scoped_enables=enables-1,unsafe_scoped_enables=len(unsafe),complete_PPU_frames=len(frames),raw_bytes=size,case_capture_events=len(caps),unique_original_case_filenames=len(lastcaps),duplicate_case_names={n:[q['wall']for q in caps if q['data']['name']==n]for n in lastcaps if sum(q['data']['name']==n for q in caps)>1},case_files_match_last_saved_raw_event=True,derived_actual_wholeframes=len(derived),sheets=len(sheets),agent_visual_review=False,missing_success_components=['native-bass-gallery.json','ppu-capture-native-result.json'],native_worker_released=True,limits=['Original aggregateFALSE staysFALSE; this is independent saved-prefix analysis.','Three initial cases reached source component transitions; full16case native summary missing, no profile pass or all32plan coverage.','Two generic buster capture names were reused for funded/empty; originals remain unchanged, all40event occurrences are separately recovered from fullraw with exact ordinal map.','First-failure ARGB comes from live line0 before completedframe1308 and cannot prove a completed visible wrap. Last full raw frame1307 retained.','Every complete DMA exact while renderingoff does not make the late rendering enable safe.','No raw VRAM/parser/producer/NMI costs in original trace. Source/diagnostic follow-up requires separate readiness/grant.','Source draw-pointer match is not effect pixel fidelity; actual selected wholeframes require separate agent review.'])
 put(a.output/'analysis.json',z)
 files=set(p for p in out.iterdir()if p.is_file());files.update(p for p in a.output.rglob('*')if p.is_file());files.update([Path(__file__),a.ready/'proof.json',a.ready/'manifest.json'])
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 put(a.output/'proof.json',dict(passed=False,preservation_passed=True,ROM_sha256=SHA,native_run=False,analysis_sha256=sha(a.output/'analysis.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),original_native_aggregate_remains_false=True,Hard_unrun=True,agent_visual_review=False))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(output=str(a.output),proof_sha256=sha(a.output/'proof.json'),analysis=z),indent=2))

if __name__=='__main__':main()
