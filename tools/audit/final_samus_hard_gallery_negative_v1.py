"""Freeze the first Samus art-observer FALSE without changing native evidence."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import SHA,ROOT
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 verify_manifest(a.ready/'manifest.json');r=json.loads((a.ready/'proof.json').read_text());n=Path(r['output']);proof=json.loads((n/'proof.json').read_text());f=json.loads((n/'first-failure.json').read_text());assert proof['passed']is False and proof['runner_exit']==1 and proof['dependencies_unchanged']and f['message']=='Actual selected body pointer is a bound Samus record'
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];setups=[e for e in events if e['kind']=='B-native-boundary-complete-setup'];assert len(setups)==1 and setups[0]['case']==1 and setups[0]['update']==1 and setups[0]['data']['owned']==0
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert len(rows)==374 and(n/'actual-ppu.argb').stat().st_size==len(rows)*245760 and all(int(z['mode'])==1 for z in rows[-4:])
 completed=starts=enables=0;last=None
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware']and not q['differences']
   assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
   last=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==last['source']and q['completed_dma_id']==last['id']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
   enables+=1;assert q['safe']
 raw=(n/'actual-ppu.argb').open('rb');sheet=Image.new('RGB',(4*272,280),(32,32,32));draw=ImageDraw.Draw(sheet);selection=[]
 for k,i in enumerate([371,372,373,374]):
  raw.seek((i-1)*245760);z=raw.read(245760);im=Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB');path=a.output/f'{i:06}.png';im.save(path);sheet.paste(im,(k*272,32));draw.text((k*272+2,2),f'Actual PPU{rows[i-1]["ppu_frame"]} / {i}',fill='white');draw.text((k*272+2,16),'Before first staged body draw',fill='white');selection.append(dict(path=str(path),sha256=sha(path),raw_slice_sha256=hashlib.sha256(z).hexdigest(),actual_PPU=rows[i-1]))
 sheet.save(a.output/'before-first-body-PPU.png');Image.frombytes('RGBA',(256,240),(n/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB').save(a.output/'first-failure-partial-snapshot.png');put(a.output/'selection.json',selection)
 facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,actual_numeric_mode=1,completed_cases=0,completed_subphases=0,complete_fixture_setups=1,original_failure=f,last_setup=setups[0],complete_PPU_frames=len(rows),complete256DMAs=completed,startFrame_records=starts,safe_scoped_enables=enables,last_complete_DMA=last['id'],native_worker_released=True,classification='Art-observer ROM-only registry rejects a source-owned filtered RAM record. First failure A126 at NativeGoombaRender Slow continuation is consistent with R1=$7E; actual pointer low and runtime filter inputs were not logged. Separate complete compiled caller reproduction is required; the original native evidence is not backfilled.',scope='No ability was exercised or completed. Saved complete frames predate the first staged body publication; first-failure image is a partial-screen snapshot, not a completed stage result. No ROM defect, acquisition, gameplay or visual pass claimed.')
 put(a.output/'facts.json',facts)
 files={Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',a.ready/'ROOT-grant.json'};files.update(q for q in n.iterdir()if q.is_file());files.update(q for q in a.output.rglob('*')if q.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),facts_sha256=sha(a.output/'facts.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),native_worker_released=True));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),counts=facts),indent=2))

if __name__=='__main__':main()
