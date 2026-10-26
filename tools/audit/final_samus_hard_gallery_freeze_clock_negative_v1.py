"""Preserve third native FALSE and actual Ice/counter boundary evidence."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil
from PIL import Image,ImageDraw
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA
from final_item_abilities_remaining731_run_v1 import verify_manifest
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=D/'current3b112-samus-hard-pool-ready-v1';assert verify_manifest(ready/'manifest.json')==992;n=ready/'native';pr=json.loads((n/'proof.json').read_text());failure=json.loads((n/'first-failure.json').read_text());assert pr['passed']is False and pr['runner_exit']==1 and pr['dependencies_unchanged']and failure['message']=='Every actual freeze update decrements exactly one'
 events=[json.loads(s)for s in(n/'events.jsonl').read_text().splitlines()];complete=[q for q in events if q['kind']=='samus-subphase-complete'];freeze=next(q for q in events if q['kind']=='actual-Ice-freeze');assert len(complete)==15 and freeze['data']['ticks']==360 and freeze['update']==1117 and freeze['wall']==1491
 rows=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')));assert len(rows)==1596 and(n/'actual-ppu.argb').stat().st_size==len(rows)*245760 and int(rows[-1]['updates'])==1221
 raw=(n/'actual-ppu.argb').open('rb')
 def data(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 old=D/'current3b112-samus-hard-outline-ready-v2/native';other=(old/'actual-ppu.argb').open('rb');h=hashlib.sha256();g=hashlib.sha256()
 for i in range(1,1469):z=data(i);y=other.read(245760);assert y==z,('actual PPU prefix',i);h.update(z);g.update(y)
 assert h.hexdigest()==g.hexdigest()
 oldevents=[json.loads(s)for s in(old/'events.jsonl').read_text().splitlines()];assert[q for q in events if q['wall']<=1467]==[q for q in oldevents if q['wall']<=1467]
 completed=starts=enables=0;last=None
 for line in(n/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']=='completed-DMA-before-render-enable':
   completed+=1;assert q['id']==completed and len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware']and not q['differences'];assert q['start']['pc']==0xe005 and q['complete']['pc']==0xe008 and q['start']['oamaddr']==q['complete']['oamaddr']==0 and q['start']['mask']&24==q['complete']['mask']&24==0
   for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['value']==q['source'][i]and w['stamp']['mask']&24==0
   last=q
  elif q['kind']=='startFrame-hardware':
   starts+=1;assert len(q['hardware'])==256
   if q.get('completed_dma_id')and not q.get('pending_dma_id'):assert q['hardware']==last['source']and q['completed_dma_id']==last['id']
  elif q['kind']=='actual-PPUMASK-write'and q['scoped']and q['enabling']:enables+=1;assert q['safe']
 assert(completed,starts,enables)==(1558,1596,1241)
 chosen=[(1469,'Full missile pool setup'),(1475,'Fresh Select refused'),(1481,'Missile pool complete'),(1482,'Ice setup'),(1488,'Ice spawn'),(1489,'Ice visible +2 sample'),(1492,'Actual freeze admission'),(1493,'Subsequent visible frame'),(1494,'Subsequent visible frame'),(1582,'Source held checkpoint'),(1595,'Before borrow failure'),(1596,'Last complete actual PPU')]
 im=Image.new('RGB',(4*272,3*280),(32,32,32));draw=ImageDraw.Draw(im);selection=[]
 for k,(i,label)in enumerate(chosen):
  z=data(i);pic=Image.frombytes('RGBA',(256,240),z,'raw','BGRA').convert('RGB');x=k%4*272;y=k//4*280;im.paste(pic,(x,y+32));draw.text((x+2,y+1),f'Actual PPU{rows[i-1]["ppu_frame"]}/ordinal{i}',fill='white');draw.text((x+2,y+15),label,fill='white');selection.append(dict(ordinal=i,actual_PPU=rows[i-1],label=label,x=x,y=y+32,width=256,height=240,raw_slice_sha256=hashlib.sha256(z).hexdigest()))
 im.save(a.output/'pool-Ice-whole-PPU.png');Image.frombytes('RGBA',(256,240),(n/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB').save(a.output/'first-failure-partial.png');put(a.output/'selection.json',selection)
 facts=dict(native_aggregate_remains_FALSE=True,original_native_proof_sha256=sha(n/'proof.json'),dependencies_unchanged=True,ROM_sha256=SHA,mode=1,completed_cases=[1,2,3,4],completed_subphases=15,uncompleted_case=5,unrun_cases=[6,7,8],original_failure=failure,actual_freeze=freeze,last_complete_PPU=rows[-1],failure_update_inferred_next=1222,complete256DMAs=completed,startFrames=starts,safe_scoped_enables=enables,prefix_actual_PPU_frames_equal=1468,prefix_actual_bytes=1468*245760,prefix_raw_sha256=h.hexdigest(),prefix_events_semantically_equal_through_wall=1467,actual_timer_operands_dumped=False,source_conclusion='CallerAB6A borrows high byte before leafBFD2. Separate complete CPU trace proves full256→leafpartial0→after255 at genuine returnAB80; native first failure atAB80/A255 after source-created360/update1117 and nextupdate1222 matches this boundary. Native low/high operands were not recorded and are not backfilled. No timer/game defect is proved.',scope='B controlled seeds/use, not acquisition. Original exact360count/STOP/pose/thaw completion remains required. Native first4case prefix is observed, wholeunit remainsFALSE; no Ice fullthaw/break/Wave/Varia/Screw/wholepixel/FPS/audio pass.',worker_released=True)
 put(a.output/'facts.json',facts);put(a.output/'chronology.json',dict(completed=complete,Ice=[q for q in events if q['case']==5]))
 files={Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant.json'};files.update(q for q in n.iterdir()if q.is_file());files.update(q for q in a.output.iterdir()if q.is_file());put(a.output/'manifest.json',dict(bindings=[dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q))for q in sorted(files,key=str)]));verify_manifest(a.output/'manifest.json');put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,original_native_proof_sha256=sha(n/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),facts_sha256=sha(a.output/'facts.json'),bindings=len(files),worker_released=True));print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),prefix_raw_sha256=h.hexdigest()),indent=2))
if __name__=='__main__':main()
