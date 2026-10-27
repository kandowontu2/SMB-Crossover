"""Freeze one exact combined Bill profile and full-frame review sheets, offline."""
from pathlib import Path
import argparse,csv,json,shutil
from final_bill_lance_combined_prepare_v3 import D,ROOT,SHA,sha,put
from final_item_abilities_remaining731_run_v1 import verify_manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    base=D/'final-bill-lance-combined-ce635-ready-v3';ready=base/'final-freeze-v4/bill-hard';native=base/'profiles/bill-hard/native'
    n=json.loads((native/'proof.json').read_text());assert n['passed'] and n['ROM_sha256']==SHA and n['runner_exit']==0 and n['dependencies_unchanged'] and n['worker_released'] and n['launches']==1 and n['retries']==0
    assert verify_manifest(ready/'manifest.json')==1028
    assert not(base/'profiles/lance-hard/native/launch.json').exists()
    hardware=n['analysis']['components']['hardware'];cadence=n['analysis']['components']['cadence']
    assert hardware['complete256DMAs']==3574 and hardware['safe_scoped_enables']==3248 and cadence['entries']==3860 and cadence['finishes']==3859
    observed=json.loads((native/'native-bill-gallery.json').read_text());hud=json.loads((native/'combined-bill-hud.json').read_text())
    assert observed['actual_variant_readback']==0 and observed['actual_mode_readback']==1 and len(observed['cases'])==7
    assert hud['genuine_render_returns']==2533 and hud['actual_OAM_stores']==30396 and hud['foreign_renders_refused']==4979
    # Independent raw physical-transfer replay, without invoking/weakening the
    # original collector or replacing any serialized old outcomes.
    dma=enables=0
    for line in(native/'ability-dma-epochs.jsonl').open():
        row=json.loads(line)
        if row['kind']=='completed-DMA-before-render-enable':
            dma+=1;assert len(row['source'])==len(row['hardware'])==len(row['writes'])==256 and row['source']==row['hardware'] and not row['differences']
            assert [w['value']for w in row['writes']]==row['source']
        elif row['kind']=='actual-PPUMASK-write'and row['scoped']and row['enabling']:
            enables+=1;s=row['stamp'];assert row['safe']and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
    assert(dma,enables)==(3574,3248)
    captures={}
    for line in(native/'events.jsonl').open():
        event=json.loads(line)
        if event['kind']=='ppu-frame-captured':captures[event['data']['name']]=event
    names=[q['q']['name']for q in observed['cases']]
    from PIL import Image,ImageDraw
    sheets=[];placements=[]
    for suffix,title in [('committed-HUD','actual committed HUD'),('1-source-art','right free shot'),('2-source-art','left contact shot'),('3-source-art','right terrain shot'),('4-source-art','left second-edge / held cadence')]:
        sheet=Image.new('RGB',(3*272,3*276),(24,44,75));draw=ImageDraw.Draw(sheet)
        for i,name in enumerate(names):
            key=name+'-'+suffix;src=native/(key+'.argb');assert src.stat().st_size==245760
            im=Image.frombytes('RGBA',(256,240),src.read_bytes(),'raw','BGRA').convert('RGB');x=(i%3)*272+8;y=(i//3)*276+28
            draw.rectangle((x-3,y-3,x+258,y+242),outline=(80,196,224),width=2);sheet.paste(im,(x,y));draw.text((x,y-20),name,fill=(255,255,255))
            placements.append(dict(case=name,kind=title,source=str(src),sha256=sha(src),native_capture_event=captures[key],sheet=suffix+'.png',box=[x,y,x+256,y+240]))
        path=a.output/(suffix+'.png');sheet.save(path);sheets.append(dict(path=str(path),sha256=sha(path),placements=7))
    cases=[]
    for q in observed['cases']:
        stages=[]
        for s in q['stages']:
            assert s['passed']and s['naturalPoolEmpty']
            stages.append({k:s[k]for k in ['kind','face','draws','hits','damageCalls','impacts','naturalPoolEmpty'] if k in s}|dict(actual_emission_velocities=[v['vx']for v in s['spawns']],emission_updates=[v['update']for v in s['spawns']],groundCrossed=s.get('groundCrossed')))
        cases.append(dict(name=q['q']['name'],actual_grants=[g['item']for g in q['grants']],expected_owned=q['q']['expected_owned'],expected_selected=q['q']['expected_selected'],source_shot_type=q['q']['shot_type'],collect_calls=q['collectCalls'],stages=stages))
    put(a.output/'case-summary.json',dict(cases=cases,scope='Actual ce635 B controlled legal use, not natural block/rise/random acquisition or waveform.'))
    put(a.output/'visual-placements.json',dict(placements=placements,sheets=sheets,agent_visual_review_pending=True,every_frame_visual_review=False))
    receipt=dict(passed=True,native_run=True,ROM_sha256=SHA,profile='bill-hard',actual_mode=1,actual_variant=0,launches=1,retries=0,worker_released=True,Lance_unrun=True,
        cases=7,use_components=28,physical_mature_item_grants=7,hardware=hardware,independent_raw_DMA_reparse=dict(passed=True,full256DMAs=dma,safe_enables=enables),
        cadence=cadence,actual_full_PPU=n['analysis']['components']['actual_full_PPU'],actual_HUD=hud,
        native_counters={k:observed[k]for k in ['minSP','nmis','irq_scroll_stores','hardware_chr_checks','complete_dma_checks','apuWrites']},
        human_GUI_context_before=n['human_GUI_context_before'],human_GUI_context_after=n['human_GUI_context_after'],human_GUI_is_informational_only=True,
        original_native_receipt=dict(path=str(native/'proof.json'),sha256=sha(native/'proof.json'),bytes=(native/'proof.json').stat().st_size),
        original_first_combined_FALSE_retained=True,source_ready_sha256=sha(ready/'proof.json'),grant_sha256=sha(ready/'ROOT-grant-bill-hard.json'),
        scope='Exact private ce635 Bill Hard finite gallery only. No Lance/other-character/campaign/adoption/waveform/zero-lag claim. Selected35 whole frames supplied for review; no every-frame visual certification.')
    put(a.output/'proof.json',receipt)
    files={Path(__file__),ready/'proof.json',ready/'manifest.json',ready/'ROOT-grant-bill-hard.json'}
    files.update(Path(q['path'])for q in json.loads((ready/'manifest.json').read_text())['bindings'])
    files.update(f for f in native.iterdir()if f.is_file())
    files.update(f for f in a.output.iterdir()if f.is_file())
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    print(json.dumps(dict(passed=True,worker_released=True,proof_sha256=sha(a.output/'proof.json'),bindings=len(files),whole_frame_placements=35,source_mode_and_native_scope='ce635 Bill Hard only')))


if __name__=='__main__':main()
