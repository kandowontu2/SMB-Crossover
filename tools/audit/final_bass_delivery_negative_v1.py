"""Freeze the one unchanged four-reward negative; no native execution or edits."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_bass_delivery_run_v1 import SHA
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 verify_manifest(a.ready/'manifest.json');ready=json.loads((a.ready/'proof.json').read_text());native=Path(ready['output']);n=json.loads((native/'proof.json').read_text());failure=json.loads((native/'first-failure.json').read_text());assert n['passed']is False and n['runner_exit']==1 and n['dependencies_unchanged']and failure['message']=='Exact private48-active-update/16pixel rise'
 events=[json.loads(s)for s in(native/'events.jsonl').read_text().splitlines()];completed=[q for q in events if q['kind']=='physical-reward-completed'];prepared=[q for q in events if q['kind']=='actual-reward-prepared'];assert len(completed)==1 and completed[0]['data']['item']==0 and completed[0]['data']['transformCalls']==60 and [q['data']['item']for q in prepared]==[0,2]
 frames=list(csv.DictReader((native/'actual-ppu-index.csv').open(newline='')));assert [int(q['ordinal'])for q in frames]==list(range(1,len(frames)+1));assert (native/'actual-ppu.argb').stat().st_size==len(frames)*245760 and len(frames)==884
 raw=(native/'actual-ppu.argb').open('rb')
 def data(i):raw.seek((i-1)*245760);z=raw.read(245760);assert len(z)==245760;return z
 captures=[q for q in events if q['kind']=='ppu-frame-captured']
 for q in captures:assert (native/(q['data']['name']+'.argb')).read_bytes()==data(q['wall'])
 hardware=n['analysis']['components']['actual_hardware'];assert hardware['passed']and hardware['complete256DMAs']==771 and hardware['safe_enables']==459
 icon=[];last=None
 for line in(native/'ability-dma-epochs.jsonl').open():
  q=json.loads(line)
  if q['kind']!='completed-DMA-before-render-enable':continue
  assert q['source']==q['hardware']and len(q['source'])==len(q['writes'])==256 and not q['differences'];last=q
  if q['start']['frame']<828:continue
  parts=[]
  for i in range(0,256,4):
   y,t,attr,x=q['source'][i:i+4]
   if (t,x)in[(31,112),(43,120),(51,113),(55,121)]and y<240:parts.append(dict(slot=i//4,y=y,tile=t,attr=attr,x=x))
  if parts:icon.append(dict(DMA=q['id'],actual_start=q['start'],actual_complete=q['complete'],parts=parts))
 assert last['id']==771 and icon[-1]['parts'][-1]['y']==145
 put(a.output/'actual-METAL-published-icon-chronology.json',icon)
 chosen=[(371,'mushroom reveal'),(400,'mushroom rising'),(437,'mushroom mature'),(468,'contact alignment'),(474,'transform age6'),(498,'transform age30'),(528,'native tier commit'),(588,'buster HUD'),(595,'actual buster effect'),(811,'natural cleanup'),(819,'reward1 complete'),(833,'METAL reveal'),(836,'METAL first published'),(844,'METAL rising'),(860,'METAL rising'),(876,'METAL rising'),(880,'METAL rising'),(884,'last completed PPU')]
 sheet=Image.new('RGB',(4*272,5*280),(32,32,32));draw=ImageDraw.Draw(sheet);placements=[]
 for k,(i,label)in enumerate(chosen):
  im=Image.frombytes('RGBA',(256,240),data(i),'raw','BGRA').convert('RGB');f=a.output/f'{i:06}.png';im.save(f);x=k%4*272;y=k//4*280;sheet.paste(im,(x,y+32));draw.text((x+2,y+1),f'PPU {frames[i-1]["ppu_frame"]} / ordinal{i}',fill='white');draw.text((x+2,y+15),label,fill='white');placements.append(dict(path=str(f),sha256=sha(f),raw_slice_sha256=hashlib.sha256(data(i)).hexdigest(),actual_PPU=frames[i-1],label=label,x=x,y=y+32,width=256,height=240))
 sheet.save(a.output/'whole-PPU-negative-contact.png');put(a.output/'selection.json',placements)
 im=Image.frombytes('RGBA',(256,240),(native/'first-failure.argb').read_bytes(),'raw','BGRA').convert('RGB');im.save(a.output/'first-failure-partial-snapshot.png')
 facts=dict(native_aggregate_remains_FALSE=True,ROM_sha256=SHA,actual_mode=0,observed_reward_list=[dict(item=q['data']['item'],prng=q['data']['prng'],prepare_wall=q['wall'],update=q['update'])for q in prepared],completed_reward=completed[0],uncompleted=[2,3,4],original_failure=failure,completed_PPU_frames=len(frames),complete256DMAs=771,safe_enables=459,native_worker_released=True,source_conclusion='No proven ROM defect. Original conjunction lacks terminal riseCalls/currentY operand dumps. Actual source initializes state1/phase0 and matures after16decrements/48accepted increments. Saved icon first Y160 at836 and last Y145 at884 indicate source-rendered actorY152 then137 (native originY+24 plus signedrecordY-16); mature failure occurs later atPPU885. This bounds presentation, not an exact missing terminal RAM/counter reconstruction.',observer_limit='Original entry-only count may include nonaccepted/revisited entry; actual count/terminalstate/Y not preserved. Do not assert which conjunction operand failed. Need narrow actual write/accepted-return observation before resolving count.',scope='ONE failed four-reward fixture, mushroom lifecycle60transform/use passes observed; METAL reveal/source icon/rise partial only. No third/fourth reward, BALANCE/refill, all-item, Hard, lag/FPS/wholepixel/sourceaudio closure. Staged post-rise downward contact remains explicit.')
 put(a.output/'facts.json',facts)
 files={Path(__file__),a.ready/'proof.json',a.ready/'manifest.json',a.ready/'ROOT-grant.json'};files.update(q for q in native.iterdir()if q.is_file());files.update(q for q in a.output.rglob('*')if q.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]));put(a.output/'proof.json',dict(passed=True,negative_preserved=True,native_aggregate_remains_FALSE=True,agent_visual_review=False,ROM_sha256=SHA,native_proof_sha256=sha(native/'proof.json'),facts_sha256=sha(a.output/'facts.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),native_worker_released=True));verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files)),indent=2))

if __name__=='__main__':main()
