"""Freeze the fourth native FALSE without changing the saved Wave observation."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=D/'current3b112-samus-hard-freeze-clock-ready-v1';assert verify_manifest(ready/'manifest.json')==1020;n=ready/'native';proof=json.loads((n/'proof.json').read_text());fail=json.loads((n/'first-failure.json').read_text());assert not proof['passed'] and proof['runner_exit']==1 and proof['dependencies_unchanged'] and fail['message']=='Actual upward Wave keeps complete world page'
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];done=[q for q in events if q['kind']=='samus-subphase-complete'];assert len(done)==17 and done[-1]['case']==5
 clock=[q for q in events if q['kind']=='actual-full-freeze-clock-boundary'];thaw=[q for q in events if q['kind']=='actual-Ice-thaw'];assert len(clock)==2 and len(thaw)==1 and thaw[0]['data']['steps']==360
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert len(rows)==1903 and(n/'actual-ppu.argb').stat().st_size==1903*245760
 raw=(n/'actual-ppu.argb').open('rb')
 def frame(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 old=D/'current3b112-samus-hard-pool-ready-v1/native';h=hashlib.sha256()
 with(old/'actual-ppu.argb').open('rb')as f:
  for i in range(1,1597):z=frame(i);assert f.read(245760)==z,('PPU prefix',i);h.update(z)
 prior=[json.loads(s)for s in(old/'events.jsonl').read_text().splitlines()];assert[q for q in events if q['wall']<=1595]==[q for q in prior if q['wall']<=1595]
 completed=starts=enables=0;last=None
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware'] and not q['differences'];assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i] and w['stamp']['mask']&24==0
   last=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;assert len(q['hardware'])==256
   if q.get('completed_dma_id') and not q.get('pending_dma_id'):assert q['hardware']==last['source'] and q['completed_dma_id']==last['id']
  elif q['kind']=='actual-PPUMASK-write' and q['scoped'] and q['enabling']:enables+=1;assert q['safe']
 assert(completed,starts,enables)==(1861,1903,1544)
 chosen=[(1582,'Ice held'),(1843,'Ice held near natural thaw'),(1852,'Actual 360th tick / thaw'),(1853,'Second Ice setup'),(1859,'Second Ice shot'),(1867,'Second native freeze'),(1893,'Fresh shot into frozen target'),(1897,'Native break then damage'),(1898,'Wave original setup'),(1899,'After original setup'),(1902,'Before first Wave shot'),(1903,'Last complete PPU')]
 sheet=Image.new('RGB',(4*272,3*280),(32,32,32));draw=ImageDraw.Draw(sheet);selection=[]
 for k,(i,label)in enumerate(chosen):
  z=frame(i);x=k%4*272;y=k//4*280;sheet.paste(Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB'),(x,y+32));draw.text((x+2,y+1),f'Actual PPU{rows[i-1]["ppu_frame"]}/ordinal{i}',fill='white');draw.text((x+2,y+15),label,fill='white');selection.append(dict(ordinal=i,actual_PPU=rows[i-1],label=label,x=x,y=y+32,width=256,height=240,raw_slice_sha256=hashlib.sha256(z).hexdigest()))
 sheet.save(a.output/'Ice-Wave-original-whole-PPU.png');Image.frombytes('RGBA',(256,240),(n/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB').save(a.output/'first-failure-partial.png');put(a.output/'selection.json',selection)
 chronology=dict(completed=done,Ice=[q for q in events if q['case']==5 and q['kind'] not in ['actual-Samus-art','ppu-frame-captured']],Wave=[q for q in events if q['case']==6]);put(a.output/'chronology.json',chronology)
 facts=dict(native_aggregate_remains_FALSE=True,original_native_proof_sha256=sha(n/'proof.json'),ROM_sha256=SHA,mode=1,completed_cases=5,completed_subphases=17,uncompleted_case=6,unrun_cases=[7,8],failure=fail,complete256DMAs=completed,startFrames=starts,safe_scoped_enables=enables,actual_PPU_frames=1903,prefix_actual_frames_equal=1596,prefix_raw_sha256=h.hexdigest(),prefix_events_equal_through_wall=1595,actual_clock_boundaries=clock,actual_thaw=thaw,source_only_reconstruction='Full GameLoop with original logicalrow9 block clamps playerX before first shot. CPU reproduction yields world265/261 rather than configured254/258. Native firstMove position operands were not recorded and are not backfilled. Moving only the authored block to logicalrow7 removes that overlap in full-caller CPU controls.',scope='B controlled ability use, not acquisition. First5cases observed; whole8case aggregate staysFALSE. No Wave/Varia/Screw native completion, audio waveform, wholepixel or global timing closure.',worker_released=True)
 put(a.output/'facts.json',facts)
 refs=[Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant.json',D/'current3b112-samus-hard-wave-prefix-v2/proof.json',D/'current3b112-samus-hard-wave-prefix-v3/proof.json',D/'current3b112-samus-hard-wave-ready-v1/proof.json',D/'current3b112-samus-hard-wave-ready-v1/fixture.patch']
 refs+=list(q for q in n.iterdir()if q.is_file());refs+=list(a.output.iterdir());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(set(refs),key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(set(refs)),worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),prefix_raw_sha256=h.hexdigest()),indent=2))
if __name__=='__main__':main()
