"""Read-only actual remaining-profile731 integrity and finite whole-PPU sheets."""
from pathlib import Path
import argparse,collections,csv,hashlib,json
from PIL import Image,ImageDraw,ImageFont
from final_item_abilities_remaining731_run_v1 import verify_manifest,PROFILES
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FRAME=256*240*4

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--profile',choices=sorted(PROFILES),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==CURRENT;bound=verify_manifest(a.ready/'manifest.json');profile=next(q for q in ready['profiles']if q['profile']==a.profile);native=Path(profile['output'])
 proof=json.loads((native/'proof.json').read_text());n=json.loads((native/'native-abilities.json').read_text());family,hard,mode,casecount=PROFILES[a.profile];assert proof['passed']and proof['runner_exit']==0 and n['actual_mode_readback']==mode and n['hard']is hard and n['family']==family and len(n['abilities'])==casecount
 index=list(csv.DictReader((native/'actual-ppu-index.csv').open()));assert len(index)>100 and(native/'actual-ppu.argb').stat().st_size==len(index)*FRAME
 raw_hashes=[];by_ordinal={int(q['ordinal']):q for q in index};rawdigest=hashlib.sha256()
 with(native/'actual-ppu.argb').open('rb')as f:
  for i,row in enumerate(index,1):
   data=f.read(FRAME);assert len(data)==FRAME and int(row['ordinal'])==i
   rawdigest.update(data);raw_hashes.append(hashlib.sha256(data).hexdigest())
  assert not f.read(1)
 assert rawdigest.hexdigest()==proof['analysis']['full_PPU_raw_index']['raw_sha256']
 events=[json.loads(line)for line in(native/'events.jsonl').read_text().splitlines()]
 telemetry=[{k:int(v)if k not in['kind']else v for k,v in r.items()}for r in csv.DictReader((native/'ability-updates.csv').open())]
 captures=[]
 for e in events:
  if e['kind']!='ppu-frame-captured':continue
  ordinal=e['wall'];file=native/(e['data']['name']+'.argb');assert sha(file)==raw_hashes[ordinal-1]
  captures.append(dict(case_capture=str(file),sha256=sha(file),source_queue=e['data'],recorded_endFrame_wall=ordinal,actual_PPU_index=by_ordinal[ordinal],actual_slice_sha256=raw_hashes[ordinal-1]))
 assert captures
 dmas={};start_frames={};counts=collections.Counter();bad=[];scoped_enables=[];pending_start=[]
 with(native/'ability-dma-epochs.jsonl').open()as f:
  for line in f:
   q=json.loads(line);kind=q['kind'];counts[kind]+=1
   if kind=='completed-DMA-before-render-enable':
    assert q['id']==len(dmas)+1 and q['page']==2 and q['start']['pc']==0xe005 and q['complete']['pc']==0xe008
    assert len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and not q['differences']
    assert q['source']==q['hardware'] and q['start']['oamaddr']==q['complete']['oamaddr']==0
    assert q['start']['mask']&24==q['complete']['mask']&24==0
    for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0 and w['value']==q['source'][i]
    dmas[q['id']]=dict(start=q['start'],complete=q['complete'],source=q['source'],hardware=q['hardware'],source_publication_match=q['source_publication_match'])
   elif kind=='startFrame-hardware':
    frame=q['stamp']['frame'];assert frame not in start_frames;start_frames[frame]=q
    assert len(q['hardware'])==256
    if q.get('pending_dma_id'):pending_start.append(q)
    elif q.get('completed_dma_id'):assert q['hardware']==dmas[q['completed_dma_id']]['source']
   elif kind=='actual-PPUMASK-write'and q['scoped']and q['enabling']:
    s=q['stamp'];assert q['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274);scoped_enables.append(q)
 expected=proof['analysis']['independent_actual_DMA_timing'];assert len(dmas)==expected['complete256_epochs']and len(start_frames)==expected['startFrame_snapshots']and len(scoped_enables)==expected['scoped_safe_enables']
 groups=[]
 for i,q in enumerate(n['physical_collections'],1):
  assert q['transformCalls']==60 and q['ownerCalls']==q['beginCalls']==1 and q['staged']<q['revealed']<q['mature']<q['collisionPlaced']<q['collected']
  walls=[(q['staged'],'staged block'),(q['revealed'],'reveal'),(q['revealed']+24,'rising'),(q['mature'],'full rise'),(q['collisionPlaced']-1,'before contact alignment'),(q['collisionPlaced'],'physical owner'),(q['collisionPlaced']+5,'transform age6'),(q['collisionPlaced']+29,'transform age30'),(q['collected']-1,'before tier commit'),(q['collected'],'tier commit'),(q['collected']+1,'committed tier'),(q['collected']+4,'settled tier')]
  groups.append(dict(name=f'pickup-{i}',description='Actual staged head/block/reveal/fullrise; disclosed post-rise contact alignment and60-update transform.',walls=walls))
 for i,q in enumerate(n['abilities'],1):
  rows=[r for r in telemetry if r['case']==i];assert rows and rows[0]['wall']==q['started']
  if q['q']['kind']=='hammer':
   hit=next(e['wall']for e in events if e['kind']=='actual-ability-damage-entry'and q['started']<=e['wall']<=q['finished'])
   walls=[(q['started'],'arena/start'),(q['started']+5,'Select attack'),(hit-1,'before real hit'),(hit,'real hit/defeat'),(hit+1,'hit display+1'),(hit+3,'hit display+3'),(hit+6,'after hit'),(q['started']+25,'native cleanup'),(q['finished'],'completed/idle')]
  elif q['q']['kind']in ['disk_free','disk_hit']:
   live=[r for r in rows if r['reach']>=24];assert live
   peak=next(r['wall']for r in live if r['reach']==q['q']['reach'])
   returning=next(r['wall']for r in live if r['returning']==1)
   catch=next(e['wall']for e in events if e['kind']=='actual-native-disk-catch'and q['started']<=e['wall']<=q['finished'])
   walls=[(q['started'],'arena/start'),(q['started']+5,'B input/windup'),(live[0]['wall'],'first extension'),(peak,'acquired max reach'),(returning,'native retraction'),(catch-1,'before catch'),(catch,'real catch'),(catch+2,'catch display'),(q['finished'],'completed/cleanup')]
   if q['q']['kind']=='disk_hit':
    hit=next(e['wall']for e in events if e['kind']=='actual-ability-damage-entry'and q['started']<=e['wall']<=q['finished'])
    walls +=[(hit-1,'before disk hit'),(hit,'real disk hit'),(hit+2,'hit display')]
  elif q['q']['kind']=='flight_gate':
   walls=[(q['started']+age,f'age{age} refusal/land')for age in[0,5,10,17,20,30,50,80,190]]
  elif q['q']['kind']=='flight_full':
   ages=[0,5,16,17,30,45,60,74,75,76,90,120,136,137,138,140,145,160,350]
   walls=[(q['started']+age,f'age{age} flight/exhaust/recharge')for age in ages]
  elif q['q']['kind']=='pogo_ground':
   bounces=[e['wall']for e in events if e['kind']=='actual-native-pogo-bounce-entry'and q['started']<=e['wall']<=q['finished']];assert len(bounces)>=2
   walls=[(q['started'],'arena/start'),(q['started']+5,'real A jump'),(q['started']+15,'Down+B hold'),(bounces[0],'first ground rebound'),(bounces[0]+2,'first rebound display'),(bounces[1],'second ground rebound'),(bounces[1]+2,'second rebound display'),(q['started']+169,'last held pogo'),(q['started']+170,'release input'),(q['started']+175,'release display'),(q['finished'],'completed/grounded')]
  elif q['q']['kind']=='pogo_enemy':
   staged=next(e['wall']for e in events if e['kind']=='ability-target-staged'and q['started']<=e['wall']<=q['finished'])
   hit=next(e['wall']for e in events if e['kind']=='actual-ability-damage-entry'and q['started']<=e['wall']<=q['finished'])
   bounce=next(e['wall']for e in events if e['kind']=='actual-native-pogo-bounce-entry'and q['started']<=e['wall']<=q['finished'])
   walls=[(q['started'],'arena/start'),(q['started']+5,'real A jump'),(q['started']+15,'airborne pogo input'),(staged,'separated target intro'),(hit-1,'before descending hit'),(hit,'real pogo enemy hit'),(bounce,'native rebound'),(bounce+2,'rebound display'),(bounce+6,'release/cleanup'),(q['finished'],'completed/grounded')]
  else:walls=[(q['started']+age,f'age{age} partial/release/recharge')for age in[0,5,16,17,30,34,35,36,60,79,80,81,100,240]]
  groups.append(dict(name=f'ability-{i:02d}-{q["q"]["name"]}',description=q['q']['name'],walls=walls))
 selected={}
 for group in groups:
  group['placements']=[]
  for wall,label in group.pop('walls'):
   ordinal=wall+1;assert ordinal in by_ordinal
   selected.setdefault(ordinal,[]).append(group['name']+': '+label)
   group['placements'].append(dict(ordinal=ordinal,label=label,foreground_wall=wall,actual_PPU_frame=int(by_ordinal[ordinal]['ppu_frame'])))
 images=a.output/'frames';images.mkdir();frame_bindings=[]
 with(native/'actual-ppu.argb').open('rb')as f:
  for ordinal,reasons in sorted(selected.items()):
   f.seek((ordinal-1)*FRAME);raw=f.read(FRAME);h=hashlib.sha256(raw).hexdigest();assert h==raw_hashes[ordinal-1]
   image=Image.frombytes('RGBA',(256,240),raw,'raw','BGRA').convert('RGB');path=images/f'{ordinal:06d}.png';image.save(path)
   frame=int(by_ordinal[ordinal]['ppu_frame']);owner=start_frames.get(frame)
   frame_bindings.append(dict(ordinal=ordinal,actual_PPU_index=by_ordinal[ordinal],raw_slice_sha256=h,PNG=str(path),PNG_sha256=sha(path),reasons=reasons,startFrame_owner=owner,completed_DMA=dmas.get(owner.get('completed_dma_id'))if owner else None))
 font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',12);sheets=[]
 for group in groups:
  panels=group['placements'];cols=3 if len(panels)<=12 else 4;rows=(len(panels)+cols-1)//cols
  sheet=Image.new('RGB',(cols*256,rows*270),(240,240,240));draw=ImageDraw.Draw(sheet)
  for i,q in enumerate(panels):
   x=(i%cols)*256;y=(i//cols)*270
   draw.text((x+3,y+2),f"PPU{q['actual_PPU_frame']} ord{q['ordinal']} {q['label'][:18]}",font=font,fill=(0,0,0));sheet.paste(Image.open(images/f"{q['ordinal']:06d}.png"),(x,y+30))
  path=a.output/(group['name']+'.png');sheet.save(path);sheets.append(dict(name=group['name'],path=str(path),sha256=sha(path),placements=panels))
 facts=dict(passed=True,ROM_sha256=CURRENT,profile=a.profile,native_launches_this_tool=0,native_proof_sha256=sha(native/'proof.json'),ready_sha256=sha(a.ready/'proof.json'),ready_bindings_verified=bound,actual_mode=mode,source_event_to_capture_mapping='Recorder executes immediately before original endFrame wall increment; ordinal=recorded capture-event wall, confirmed exact for every original case screenshot. Foreground event/telemetry wall maps to NEXT endFrame ordinal wall+1; labels distinguish source update from displayed publication.',actual_full_PPU_frames=len(index),full_raw_sha256=rawdigest.hexdigest(),full_raw_bytes=len(index)*FRAME,all_case_captures_exact=captures,completed_full256_DMAS=len(dmas),data_write_checks=len(dmas)*256,startFrame_snapshots=len(start_frames),pending_startFrame_count=len(pending_start),scoped_safe_render_enables=len(scoped_enables),selected_unique_whole_PPU_frames=len(selected),selected_placements=sum(len(g['placements'])for g in groups),frame_bindings=frame_bindings,sheets=sheets,abilities=n['abilities'],physical_collections=n['physical_collections'],event_counts=dict(collections.Counter(e['kind']for e in events)),native_counts={k:n[k]for k in ['updates','nmis','irq_scroll_stores','complete_dma_checks','hardware_chr_checks','apuWrites','minSP']},agent_visual_review=False,visual_status='Sheets emitted; actual agent image inspection must be recorded separately. Integrity is not a source-art/all-pixel/no-flicker verdict.')
 (a.output/'proof.json').write_text(json.dumps(facts,indent=2)+'\n')
 bindings=[]
 for f in list(native.iterdir())+[a.ready/'proof.json',a.ready/'manifest.json',Path(__file__)]+[f for f in a.output.rglob('*')if f.is_file()]:
  if f.is_file():bindings.append(dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size))
 (a.output/'manifest.json').write_text(json.dumps(dict(bindings=bindings),indent=2)+'\n')
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),frames=len(index),selected=len(selected),placements=sum(len(g['placements'])for g in groups),sheets=len(sheets),full256=len(dmas),pending_starts=len(pending_start)),indent=2))

if __name__=='__main__':main()
