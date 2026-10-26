"""Freeze literal second Samus FALSE and every saved case-image placement."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
READY=D/'current3b112-samus-hard-outline-ready-v2'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 drift=[];stable=0
 for z in json.loads((READY/'manifest.json').read_text())['bindings']:
  q=Path(z['path']);actual=dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))
  if actual['bytes']!=z['bytes']or actual['sha256']!=z['sha256']:drift.append(dict(expected=z,actual=actual))
  else:stable+=1
 assert len(drift)==1 and Path(drift[0]['actual']['path'])==READY/'emulator/Debugger/candidate.cdl'and stable==965
 put(a.output/'runtime-coverage-dependency-drift.json',dict(original_manifest_unchanged=True,original_dependencies_unchanged_remains_FALSE=True,stable_bindings=stable,drift=drift,cause='Successor copied the prior emulator tree, inadvertently binding mutable pre-existing CDL coverage. Mesen rewrote only this coverage file. Source, ROM, scripts, settings and all other bindings remain exact; no result retagging.'))
 n=READY/'native';pr=json.loads((n/'proof.json').read_text());f=json.loads((n/'first-failure.json').read_text());assert pr['passed']is False and pr['runner_exit']==1 and f['message']=='Actual shared three-slot pool refuses without cost'
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];completed=[q for q in events if q['kind']=='samus-subphase-complete'];assert len(completed)==14
 setup=next(q for q in events if q['kind']=='samus-phase'and q['phase']=='run'and q['wall']==1468);assert setup['data']['state']['ammo']==2 and setup['data']['state']['selected']==2 and all(q['type']==0 for q in setup['data']['state']['shots'])
 debit=next(q for q in events if q['kind']=='actual-missile-debit'and q['wall']==1474);spawn=next(q for q in events if q['kind']=='actual-Samus-spawn'and q['wall']==1474);assert debit['data']['before']==2 and debit['data']['after']==1 and spawn['data']['type']==41
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert len(rows)==1480 and(n/'actual-ppu.argb').stat().st_size==len(rows)*245760 and all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
 raw=(n/'actual-ppu.argb').open('rb')
 def frame(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 caps=[q for q in events if q['kind']=='ppu-frame-captured'];last={q['data']['name']:q for q in caps};saved=[]
 for name,q in last.items():
  file=n/(name+'.argb');assert file.read_bytes()==frame(q['wall']);saved.append(dict(name=name,path=str(file),sha256=sha(file),actual_ordinal=q['wall'],source_request_wall=q['data']['wall'],actual_PPU=rows[q['wall']-1]))
 assert len(caps)==106 and len(saved)==105
 complete=starts=enables=0;latest=None
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   complete+=1;assert q['id']==complete and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware']and not q['differences'];assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
   latest=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==latest['source']and q['completed_dma_id']==latest['id']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:enables+=1;assert q['safe']
 assert(complete,starts,enables)==(1446,1480,1129)
 # Every case-capture occurrence is represented, including the earlier image
 # overwritten by the deliberately unchanged repeated Long capture filename.
 chosen={}
 for q in caps:chosen.setdefault((q['case'],q['wall']),[]).append(q['data']['name'])
 for q in events:
  if q['kind']in['actual-Samus-spawn','actual-bomb-boost','actual-Samus-contact','actual-paused-selection']and q['wall']+2<=1480:chosen.setdefault((q['case'],q['wall']+2),[]).append(q['kind']+' +2 visible-epoch sample')
 sheets=[];placements=[]
 for case in range(1,5):
  selected=sorted((i,names)for(c,i),names in chosen.items()if c==case)
  for start in range(0,len(selected),12):
   batch=selected[start:start+12];im=Image.new('RGB',(4*272,((len(batch)+3)//4)*280),(32,32,32));draw=ImageDraw.Draw(im);path=a.output/f'case{case}-sheet{start//12+1}.png'
   for k,(i,names)in enumerate(batch):
    z=frame(i);picture=Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB');x=k%4*272;y=k//4*280;im.paste(picture,(x,y+32));draw.text((x+2,y+1),f'C{case} PPU{rows[i-1]["ppu_frame"]} / ordinal{i}',fill='white');draw.text((x+2,y+15),names[0][:42],fill='white');placements.append(dict(sheet=str(path),x=x,y=y+32,width=256,height=240,case=case,ordinal=i,actual_PPU=rows[i-1],labels=names,raw_slice_sha256=hashlib.sha256(z).hexdigest()))
   im.save(path);sheets.append(dict(path=str(path),sha256=sha(path),placements=len(batch)))
 Image.frombytes('RGBA',(256,240),(n/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB').save(a.output/'first-failure-partial.png')
 put(a.output/'sheets.json',sheets);put(a.output/'selection.json',placements);put(a.output/'saved-capture-integrity.json',dict(passed=True,capture_events=106,saved_files=105,overwritten_name='Long-beyond-short-range',saved=saved,scope='Last occurrence of each saved name exactly equals indexed full actual PPU. Earlier occurrence remains in raw stream and is included in sheets. Source-request wall and later actual capture epoch are separate.'))
 put(a.output/'chronology.json',dict(original_failure=f,run_setup=setup,native_debit=debit,native_spawn=spawn,completed_subphases=completed))
 facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,numeric_mode=1,completed_case_prefix=[1,2,3],completed_subphases=14,missile_case_partial=True,unrun_cases=[5,6,7,8],complete_actual_PPU_frames=1480,complete256DMA=complete,startFrames=starts,safe_scoped_enables=enables,captured_events=106,saved_capture_files=105,review_placements=len(placements),source_cause="setupTask tests only t.kind=='pool'; missile-pool therefore starts after complete pool clear without occupancy records. Native fresh Select correctly debits2→1 and spawns41. Final no-spawn/no-debit oracle is valid only with a full pool. This is a fixture initialization omission, not a proved game defect.",next_minimal_fixture_change="Seed the same complete native Long records for pool OR missile-pool; preserve all controller/seed fields, assertions and limits otherwise.",B_seeded_scope=True,acquisition=False,worker_released=True,visual_review_pending=True,limits='Whole native aggregate FALSE and missing terminal outputs remain; case completion is inferred only from emitted source finalizer events. No Ice/Wave/Varia/Screw native coverage. Actual capture-to-publication delay is explicit; no all-pixel/FPS/audio fidelity claim. Missile HUD container readability suspicion remains separately open pending actual source/pixel attribution.')
 put(a.output/'facts.json',facts)
 files={Path(__file__),READY/'proof.json',READY/'manifest.json',READY/'ROOT-grant.json'};files.update(q for q in n.iterdir()if q.is_file());files.update(q for q in a.output.rglob('*')if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),facts_sha256=sha(a.output/'facts.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),sheets=sheets,placements=len(placements)),indent=2))
if __name__=='__main__':main()
