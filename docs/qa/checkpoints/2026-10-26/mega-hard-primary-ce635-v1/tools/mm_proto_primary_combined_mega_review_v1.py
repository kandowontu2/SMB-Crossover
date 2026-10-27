"""Verify one actual ce635 MegaHard6 outcome and bind whole-frame evidence."""
from pathlib import Path
import argparse
import collections
import csv
import hashlib
import json
from PIL import Image
from mm_proto_color_rotation_native_review_v1 import sheet

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'robot-primary-combined-mega-ready-v2'
OLD=D/'mm-proto-weapon-boundary0a-v1/mega-hard-ready-v2/native'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')
rows=lambda p:[json.loads(x)for x in Path(p).read_text().splitlines()]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    for f,h in json.loads((B/'bindings.json').read_text()).items():assert sha(f)==h,f
    launch=json.loads((B/'launch-outcome-v1.json').read_text())
    assert launch['returncode']==0 and launch['strict_profile_pass']and launch['attempt']==1 and launch['no_retry']and launch['native_worker_released']
    n=B/'native';assert not(n/'first-failure.json').exists()
    result=json.loads((n/'native-mm-weapon-profile.json').read_text())
    assert result['passed']and result['actual_mode_readback']==1 and result['hard']and not result['acquisition']and not result['goal_complete']
    assert result['updates']==656 and len(result['cases'])==6
    cases=result['cases']
    for q,types,charges in zip(cases[:3],[[1],[1,2],[1,3]],[[0],[0,56],[0,87]]):
        assert[x['type']for x in q['primarySpawns']]==types and[x['charge']for x in q['primarySpawns']]==charges
        assert q['beforeAmmo']==q['finalAmmo']==[0]*7+[20]
    rush,gate,balance=cases[3:]
    assert rush['summoned']and rush['existingAttack']and rush['landed']==479 and rush['launch']==rush['bounced']==499 and rush['rushDraws']==122
    assert rush['beforeAmmo']==[0]*7+[20]and rush['finalAmmo']==[0]*7+[8]and rush['completed']==570
    assert gate['refused']and gate['beforeAmmo']==gate['finalAmmo']==[0]*7+[3]
    assert balance['balanceChoice']and balance['refillCredits']==8 and balance['completed']==656
    assert balance['beforeAmmo']==[60,4,0,0,0,0,0,8]and balance['finalAmmo']==[60,12,0,0,0,0,0,8]
    assert result['nmis']==result['irq_scroll_stores']==655 and result['hardware_chr_checks']==7860 and result['minSP']==223 and result['complete_dma_checks']==645
    events=rows(n/'events.jsonl');counts=collections.Counter(x['kind']for x in events)
    assert counts['mm-weapon-component-complete']==6 and counts['actual-rush-direct-debit']==1 and counts['actual-mm-balancer-credit']==2
    diag=rows(n/'bass-diagnostic.jsonl');entries=[x for x in diag if x['kind']=='NMI-entry']
    assert len(entries)==7 and all([x['state']['SelectedCharacter'],x['state']['ProtoVariant'],x['state']['CrossoverBehaviorVersion']]==[1,0,1]for x in entries)
    color=[x for x in diag if x.get('data',{}).get('name')=='ColorRotation'and x['stamp']['frame']==994]
    assert len(color)==2 and[color[0]['queues']['buffer1_offset'],color[1]['queues']['buffer1_offset']]==[0,7]
    assert color[1]['state']['FrameCounter']==16 and color[1]['queues']['buffer1'][:8]==[63,12,4,15,23,23,15,0]
    assert color[1]['data']['inclusive_cycles']==317
    nextnmi=next(x for x in entries if x['stamp']['frame']==995)
    assert nextnmi['queues']['buffer1_offset']==7 and nextnmi['queues']['buffer1'][:8]==color[1]['queues']['buffer1'][:8]
    epochs=rows(n/'ability-dma-epochs.jsonl');completed=[x for x in epochs if x['kind']=='completed-DMA-before-render-enable']
    assert len(completed)==997
    for x in completed:
        assert x['source']==x['hardware']and len(x['source'])==len(x['writes'])==256 and not x['differences']and x['page']==2
        assert x['start']['oamaddr']==x['complete']['oamaddr']==0 and x['start']['mask']&24==x['complete']['mask']&24==0
        for i,w in enumerate(x['writes']):assert w['value']==x['source'][i]and w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0
    scoped=[x for x in epochs if x['kind']=='actual-PPUMASK-write'and x['enabling']and x['scoped']]
    allen=[x for x in epochs if x['kind']=='actual-PPUMASK-write'and x['enabling']]
    assert len(scoped)==669 and all(x['safe']for x in allen)
    selected=[x for x in scoped if x['stamp']['frame']in[376,377,378,990,991,992,993,994,995,996]]
    capture=json.loads((n/'ppu-capture-native-result.json').read_text());frames=list(csv.DictReader((n/'actual-ppu-index.csv').open(newline='')))
    pixels=(n/'actual-ppu.argb').read_bytes();size=245760
    assert len(frames)==capture['frames']==1030 and len(pixels)==capture['bytes']==size*1030 and capture['original_done_seen']
    byframe={int(q['ppu_frame']):i for i,q in enumerate(frames)}
    def picture(frame):
        i=byframe[frame];raw=pixels[size*i:size*(i+1)]
        return Image.frombytes('RGBA',(256,240),raw,'raw','BGRA').convert('RGB'),raw
    groups=collections.defaultdict(list);samples=[];manifest={str(f):sha(f)for f in n.iterdir()if f.is_file()}
    for event in events:
        if event['kind']!='ppu-frame-captured':continue
        name=event['data']['name'];f=n/(name+'.argb');image,raw=picture(event['wall'])
        assert f.read_bytes()==raw and len(raw)==size
        manifest[str(f)]=sha(f)
        samples.append(dict(name=name,event=event,actual_PPU_row=frames[byframe[event['wall']]],raw_sha256=sha(f)))
        groups['primary'if name.startswith(('basic-','weak-','full-'))else'support'].append((name+' PPU'+str(event['wall']),image))
    assert len(samples)==34
    for name,images in groups.items():sheet(a.output/(name+'-actual-whole-images.png'),images)
    windows={};land=next(x['event']['wall']for x in samples if x['name']=='rush-lifecycle-landed')
    for name,wanted in[('rush-consecutive',range(land-3,land+33)),('startup',range(374,382)),('passive',range(990,998))]:
        images=[];data=[]
        for frame in wanted:
            image,raw=picture(frame);images.append(('Mega actual PPU'+str(frame),image));data.append(dict(frame=frame,raw_sha256=hashlib.sha256(raw).hexdigest(),actual_PPU_row=frames[byframe[frame]]))
        sheet(a.output/(name+'-actual-whole-images.png'),images);windows[name]=data
    # Passive offline comparison with the older qualified0a Mega capture. It
    # does not replace current native outcomes or constitute a new native run.
    oldframes=list(csv.DictReader((OLD/'actual-ppu-index.csv').open(newline='')));oldpixels=(OLD/'actual-ppu.argb').read_bytes()
    oldresult=json.loads((OLD/'native-mm-weapon-profile.json').read_text())
    assert oldresult['cases']==cases and len(oldframes)==len(frames)and len(oldpixels)==len(pixels)
    changes=[]
    for i,row in enumerate(frames):
        assert row['ppu_frame']==oldframes[i]['ppu_frame']
        left,right=oldpixels[i*size:(i+1)*size],pixels[i*size:(i+1)*size]
        if left!=right:
            changed=[k//4 for k in range(0,size,4)if left[k:k+4]!=right[k:k+4]]
            changes.append(dict(actual_PPU=int(row['ppu_frame']),phase=row['phase'],updates=row['updates'],
                changed_pixels=len(changed),bbox=[min(k%256 for k in changed),min(k//256 for k in changed),max(k%256 for k in changed),max(k//256 for k in changed)],
                old_raw_sha256=hashlib.sha256(left).hexdigest(),new_raw_sha256=hashlib.sha256(right).hexdigest()))
    assert len(changes)==1 and changes[0]['actual_PPU']==183 and changes[0]['phase']=='menu'and changes[0]['changed_pixels']==71 and changes[0]['bbox']==[15,45,245,47]
    menu_old=Image.frombytes('RGBA',(256,240),oldpixels[182*size:183*size],'raw','BGRA').convert('RGB')
    menu_new,_=picture(183);sheet(a.output/'old0a-vs-current-menu183-whole-images.png',[('old0a Mega PPU183',menu_old),('ce635 Mega PPU183',menu_new)])
    apu_fields=['wall','update','case','phase','register','value','pc','bank']
    oldapu=list(csv.DictReader((OLD/'apu.csv').open()));newapu=list(csv.DictReader((n/'apu.csv').open()))
    assert len(oldapu)==len(newapu)==6686
    assert[tuple(q[k]for k in apu_fields)for q in oldapu]==[tuple(q[k]for k in apu_fields)for q in newapu]
    put(a.output/'old0a-comparison.json',dict(old_ROM='0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09',
        new_ROM='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111',same_sixcase_records=True,
        full_PPU_frames=1030,byte_exact_wholeframes=1029,remaining=changes,all34stage_images_byte_exact_old0a=True,
        ordered6686_APU_fields_exact=apu_fields,CPU_cycle_stamps_differ=True,
        limits='Old0a remains old0a. No frame183 pixelidentity, waveform/subframe audio timing, matchedFPS or installation claim. Singlemenu/loading image difference is retained; no unsafe render enable exists in current all-mode logged writes.'))
    put(a.output/'native-evidence.json',dict(cases=cases,actual_variant0_Hard1_readbacks=entries,
        selected_safe_enables=selected,actual_normal_eligible_ColorRotation=color,actual_next_NMI_world_command=nextnmi,
        counter_limit='This is a normal emptyqueue FrameCounter16 append, not the Proto47B deferral or direct counter RAM readback. Counter itself unlogged; no scope merger.'))
    put(a.output/'samples.json',dict(stages=samples,windows=windows))
    for f in[B/x for x in['readiness.json','bindings.json','ROOT-grant.json','command.json','launch-binding-v1.json','launch-outcome-v1.json','launch-host-v1.log']]+[Path(__file__),OLD/'actual-ppu.argb',OLD/'actual-ppu-index.csv',OLD/'apu.csv',OLD/'native-mm-weapon-profile.json']:
        manifest[str(f)]=sha(f)
    put(a.output/'external-raw-manifest.json',manifest)
    put(a.output/'proof.json',dict(review_completed=True,native_profile_pass=True,native_launches=1,retries=0,native_worker_released=True,
        ROM_sha256='ce635f6e8793d096ba50adec9cdf1fc2dd41fd487e4acd4d0972af03af9ea111',actual_owner=1,actual_variant=0,actual_numeric_Hard=1,
        six_component_outcomes=6,source_updates=656,scoped_NMI_returns=655,physical_IRQ31_store_groups=655,hardware_CHR_checks=7860,min_SP=223,
        all_mode_full256DMA_pages=997,independent_DMA_values_and_write_positions=997*256,scoped_complete_DMA_checks=645,
        scoped_safe_enables=669,scoped_late_enables=0,all_mode_unsafe_enables=0,
        all_source_destination_pages_order_OAMADDR_disabledmask_exact=True,
        completed_full_PPU_frames=1030,completed_full_PPU_bytes=len(pixels),stage_wholeimages=34,Rush_window=36,startup_window=8,passive_window=8,paired_menu183_images=2,
        old0a_case_records_and1029wholeframes_exact=True,remaining_menu183_difference_pixels=71,APU_rows6686_ordered_fields_exact=True,cycle_stamps_not_identical=True,
        actual_source_art_callbacks=counts['actual-mm-primary-art'],agent_visual_review_pending=True,
        samples_sha256=sha(a.output/'samples.json'),evidence_sha256=sha(a.output/'native-evidence.json'),comparison_sha256=sha(a.output/'old0a-comparison.json'),
        external_manifest_sha256=sha(a.output/'external-raw-manifest.json'),tool_sha256=sha(__file__),
        limits='Fresh MegaHard6 staged use-only native, not copiedProto credit/naturalacquisition/allweapons/allroster/perfectbody/shotfairness/matchedFPS/waveform/adoption. Actual107? no invented counts; exact1030PPU. Menu183 difference retained, selected visual review separate.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),pass_=True,cases=6,DMA=997,safe_enables=669),indent=2))


if __name__=='__main__':main()
