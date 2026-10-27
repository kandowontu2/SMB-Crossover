"""Reparse the single strictdf failure and its five completed native cases."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image,ImageDraw

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2';B=C/'ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    for f,h in json.loads((B/'bindings.json').read_text()).items():assert sha(f)==h,f
    n=B/'native';outcome=json.loads((B/'launch-outcome-v1.json').read_text())
    assert outcome['returncode']==1 and not outcome['passed']and outcome['native_worker_released']and outcome['no_retry']
    assert not(n/'native-mm-weapon-profile.json').exists()
    events=[json.loads(x)for x in(n/'events.jsonl').read_text().splitlines()]
    counts=collections.Counter(x['kind']for x in events)
    cases=[x['data']for x in events if x['kind']=='mm-weapon-component-complete']
    assert len(cases)==5
    for q,types,charges in zip(cases[:3],[[1],[1,2],[1,3]],[[0],[0,56],[0,87]]):
        assert[x['type']for x in q['primarySpawns']]==types and[x['charge']for x in q['primarySpawns']]==charges
        assert q['beforeAmmo']==q['finalAmmo']==[0]*7+[20]
    rush,gate=cases[3:]
    assert rush['summoned']and rush['existingAttack']and rush['landed']==479 and rush['launch']==rush['bounced']==499
    assert rush['rushDraws']>0 and rush['beforeAmmo']==[0]*7+[20]and rush['finalAmmo']==[0]*7+[8]and rush['completed']==570
    assert gate['refused']and gate['beforeAmmo']==gate['finalAmmo']==[0]*7+[3]
    assert counts['actual-rush-direct-debit']==1 and counts['actual-mm-balancer-choice']==1 and counts['actual-mm-balancer-credit']==0
    balance=next(x for x in events if x['kind']=='actual-mm-balancer-choice')
    assert balance['data']==dict(index=18,amount=8)and balance['update']==616
    epochs=[json.loads(x)for x in(n/'ability-dma-epochs.jsonl').read_text().splitlines()]
    complete=[x for x in epochs if x['kind']=='completed-DMA-before-render-enable']
    assert len(complete)==962
    for q in complete:
        assert q['source']==q['hardware']and len(q['source'])==len(q['writes'])==256 and not q['differences']
        assert q['page']==2 and q['start']['oamaddr']==q['complete']['oamaddr']==0
        assert q['start']['mask']&24==q['complete']['mask']&24==0
        for i,w in enumerate(q['writes']):
            assert w['value']==q['source'][i]and w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0
    enables=[x for x in epochs if x['kind']=='actual-PPUMASK-write'and x['scoped']and x['enabling']]
    bad=[x for x in enables if not x['safe']]
    assert len(bad)==1 and(bad[0]['stamp']['frame'],bad[0]['stamp']['scanline'],bad[0]['stamp']['cycle'])==(993,1,57)
    startup=[x for x in enables if x['stamp']['frame']in[376,377,378]]
    assert len(startup)==3 and all(x['safe']for x in startup)
    assert[(x['stamp']['scanline'],x['stamp']['cycle'])for x in startup]==[(258,156),(257,213),(-1,264)]
    diag=[json.loads(x)for x in(n/'bass-diagnostic.jsonl').read_text().splitlines()]
    selected=next(x for x in diag if x['kind']=='NMI-entry'and x['stamp']['frame']==378)
    assert selected['state']['ProtoVariant']==selected['state']['SelectedCharacter']==selected['state']['CrossoverBehaviorVersion']==1
    assert selected['queues']['buffer1_offset']==47
    assert not any(x['stamp']['frame']==993 for x in diag)
    index=list(csv.DictReader((n/'actual-ppu-index.csv').open()))
    raw=(n/'actual-ppu.argb').read_bytes();size=256*240*4
    assert len(index)==992 and len(raw)==size*len(index)
    by_frame={int(x['ppu_frame']):i for i,x in enumerate(index)}
    samples=[];groups=collections.defaultdict(list);raw_manifest={str(x):sha(x)for x in n.iterdir()if x.is_file()}
    for event in events:
        if event['kind']!='ppu-frame-captured':continue
        name=event['data']['name'];path=n/(name+'.argb');data=path.read_bytes();frame=event['wall'];i=by_frame[frame]
        assert len(data)==size and data==raw[i*size:(i+1)*size],(name,frame)
        raw_manifest[str(path)]=sha(path)
        image=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB')
        safe=name.replace(':','-');image.save(a.output/(safe+'.png'))
        sample=dict(name=name,event=event,actual_completed_PPU=index[i],raw_sha256=sha(path),PNG_sha256=sha(a.output/(safe+'.png')))
        samples.append(sample);groups['primary'if name.startswith(('basic-','weak-','full-'))else'support'].append((sample,image))
    assert len(samples)==33
    for group,items in groups.items():
        sheet=Image.new('RGB',(1024,((len(items)+3)//4)*264),'#151923');draw=ImageDraw.Draw(sheet)
        for j,(s,image)in enumerate(items):
            x,y=j%4*256,j//4*264;sheet.paste(image,(x,y+24));draw.text((x+2,y+3),s['name']+' PPU'+str(s['event']['wall']),fill='white')
        sheet.save(a.output/(group+'-actual-whole-images.png'),optimize=True)
    land=next(x['event']['wall']for x in samples if x['name']=='rush-lifecycle-landed')
    wanted=list(range(land-3,land+33));sheet=Image.new('RGB',(1024,9*264),'#151923');draw=ImageDraw.Draw(sheet);rush_frames=[]
    for j,frame in enumerate(wanted):
        i=by_frame[frame];data=raw[i*size:(i+1)*size];image=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB')
        x,y=j%4*256,j//4*264;sheet.paste(image,(x,y+24));draw.text((x+2,y+3),'Proto actualPPU '+str(frame),fill='white')
        rush_frames.append(dict(frame=frame,row=index[i],raw_sha256=hashlib.sha256(data).hexdigest()))
    sheet.save(a.output/'rush-consecutive-actual-whole-images.png',optimize=True)
    sheet=Image.new('RGB',(1024,2*264),'#151923');draw=ImageDraw.Draw(sheet)
    startup_frames=[]
    for j,frame in enumerate(range(374,382)):
        i=by_frame[frame];data=raw[i*size:(i+1)*size];image=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB')
        x,y=j%4*256,j//4*264;sheet.paste(image,(x,y+24));draw.text((x+2,y+3),'Proto actualPPU '+str(frame),fill='white')
        startup_frames.append(dict(frame=frame,row=index[i],raw_sha256=hashlib.sha256(data).hexdigest()))
    sheet.save(a.output/'startup-actual-whole-images.png',optimize=True)
    put(a.output/'samples.json',dict(stages=samples,consecutiveRush=rush_frames,startup=startup_frames))
    put(a.output/'native-evidence.json',dict(completed_cases=cases,balance_choice=balance,startup=selected,startup_enables=startup,first_bad_enable=bad[0]))
    for f in[B/x for x in['ROOT-grant.json','readiness.json','bindings.json','command.json','launch-binding-v1.json','launch-outcome-v1.json','launch-host-v1.log']]+[Path(__file__)]:raw_manifest[str(f)]=sha(f)
    put(a.output/'external-raw-manifest.json',raw_manifest)
    put(a.output/'proof.json',dict(review_completed=True,native_profile_pass=False,ROM_sha256=sha(C/'candidate.nes'),
        native_launches=1,retries=0,native_worker_released=True,actual_mode=1,actual_variant=1,
        completed_component_cases=5,partial_case6_actual_balancer_choice=balance,no_refill_credit_or_final_case6_assertion=True,
        cases=cases,all_mode_complete_DMA_pages=962,all_mode_independently_verified_DMA_writes=962*256,
        all_full256_source_destination_write_order_OAMADDR_disabledmask_exact=True,
        scoped_safe_enables=sum(x['safe']for x in enables),scoped_bad_enables=1,
        actual_376_377_378_enables=startup,first_bad_enable=bad[0],first_failure=json.loads((n/'first-failure.json').read_text()),
        actual378_queue_offset=47,actual993_queue_parser_CHR_records_available=False,
        actual_PPU_frames=len(index),actual_PPU_bytes=len(raw),actual_stage_image_placements=33,
        consecutive_Rush_placements=36,startup_placements=8,source_art_checked_callback_events=counts['actual-mm-primary-art'],
        no_final_NMI_source_CHR_aggregate_summary=True,event_counts=dict(counts),agent_visual_review_pending=True,
        samples_sha256=sha(a.output/'samples.json'),evidence_sha256=sha(a.output/'native-evidence.json'),
        raw_manifest_sha256=sha(a.output/'external-raw-manifest.json'),tool_sha256=sha(__file__),
        limits='StrictFALSE993 held. Five completed stagedcases, no acquisition or fullsixcasepass. Original378 deadline recovered narrowly atprerender264 versus274cutoff. No actual993packet ownership captured by374..380diagnostic; do not substitute a CPU guess. No finalglobalCHR/stack/NMI aggregate.33source-time samples bound to exactwholecompletedPPU; labels can precede a requested newpublication. No matchedperformance/allweapons/wholegoal/graphicsclean claim.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),native_profile_pass=False,cases=5,DMA=962),indent=2))


if __name__=='__main__':main()
