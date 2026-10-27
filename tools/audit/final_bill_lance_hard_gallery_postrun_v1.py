"""Offline Bill/Lance gallery review; retain the original host result unchanged."""
from pathlib import Path
import argparse, copy, csv, json
from PIL import Image, ImageDraw
from final_bill_lance_hard_gallery_source_v1 import D, ROOT, SHA, put, sha
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_bill_lance_hard_gallery_run_v2 import collect as corrected_collect


def differences(a, b, path=''):
    if type(a) is not type(b):
        return [dict(path=path, native_type=type(a).__name__, native=a,
                     plan_type=type(b).__name__, plan=b)]
    if isinstance(a, dict):
        out=[]
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b:
                out.append(dict(path=path+'/'+k, missing=True))
            else:
                out += differences(a[k], b[k], path+'/'+k)
        return out
    if isinstance(a, list):
        out=[]
        if len(a)!=len(b):out.append(dict(path=path, length_mismatch=True))
        for i,(x,y) in enumerate(zip(a,b)):out += differences(x,y,path+'/'+str(i))
        return out
    return [] if a==b else [dict(path=path,native=a,plan=b)]


def literal_plan(native, plan):
    """Only the two declared NORMAL zero-length arrays have no Lua type tag."""
    assert len(native['cases'])==len(plan['cases'])==7
    diffs=[]
    for i,(q,p) in enumerate(zip(native['cases'],plan['cases'])):
        diffs += differences(q['q'],p,'case/'+str(i)+'/q')
    expected=[dict(path='case/0/q/'+key,native_type='dict',native={},plan_type='list',plan=[])
              for key in ['grant_sequence','incremental_grants']]
    assert sorted(diffs,key=lambda q:q['path'])==expected, diffs
    fixed=copy.deepcopy(native)
    for key in ['grant_sequence','incremental_grants']:
        assert fixed['cases'][0]['q'][key]=={} and plan['cases'][0][key]==[]
        fixed['cases'][0]['q'][key]=[]
    assert all(q['q']==p for q,p in zip(fixed['cases'],plan['cases']))
    return fixed,diffs


def native_cases(n,c):
    # Preserve every original collect() case predicate after the explicit,
    # schema-local empty-array interpretation. No source/outcome values masked.
    assert n['passed'] and n['actual_mode_readback']==1 and not n['acquisition']
    assert n['actual_variant_readback']==n['variant']==c['variant']
    assert len(n['cases'])==7
    rows=[]
    for q,p in zip(n['cases'],c['cases']):
        assert q['q']==p and q['completed'] and len(q['stages'])==len(p['tasks'])
        assert [z['item']for z in q['grants']]==p['incremental_grants']
        assert q['collectCalls']==len(q['grants'])
        for s,t in zip(q['stages'],p['tasks']):
            assert s['passed'] and s['completed'] and s['kind']==t['kind'] and s['face']==t['face'] and s['naturalPoolEmpty']
            assert s['spawns'] and s['draws']>0
            if t['kind']=='contact':assert s['hits']>0 and s['damageCalls']>0
            if t['kind']=='terrain':
                assert s['blockCalls']>0
                if p['terrain_behavior']=='bypass-plain-ground':assert s['groundCrossed'] and s['impacts']==0
                else:assert s['impacts']>0
        rows.append(dict(name=p['name'],completed=q['completed'],collect_calls=q['collectCalls'],
                         grants=q['grants'],stages=[{k:s[k]for k in ['kind','face','started','completed','draws','hits','damageCalls','blockCalls','impacts','naturalPoolEmpty']}for s in q['stages']]))
    assert n['nmis']>100 and n['irq_scroll_stores']>100 and n['hardware_chr_checks']>1200 and n['complete_dma_checks']>100 and n['minSP']>=128
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready',type=Path,required=True)
    p.add_argument('--profile',choices=['bill-hard','lance-hard'],required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ready=json.loads((a.ready/'proof.json').read_text())
    assert ready['ROM_sha256']==SHA and not ready['native_run']
    verified=verify_manifest(a.ready/'manifest.json')
    profile=next(q for q in ready['profiles']if q['profile']==a.profile)
    native=Path(profile['output']);original=json.loads((native/'proof.json').read_text())
    assert original['worker_released'] and original['launches']==1 and original['retries']==0 and original['dependencies_unchanged']
    assert original['ROM_sha256']==SHA and original['runner_exit']==0
    assert not(native/'first-failure.json').exists()
    n=json.loads((native/'native-bill-gallery.json').read_text());cfg=json.loads((native/'config.json').read_text())
    fixed,diffs=literal_plan(n,cfg);cases=native_cases(fixed,cfg)
    complete_collector=corrected_collect(native,cfg)
    assert complete_collector['passed'],complete_collector['errors']
    put(a.output/'full-original-collector-typed-empty-arrays.json',complete_collector)
    put(a.output/'plan-type-differences.json',dict(original_aggregate_passed=original['passed'],differences=diffs,
        explanation='The two source-proven NORMAL empty arrays are Lua empty tables. The unchanged JSON emitter has no array type tag and emits {}. Only these two exact schema paths are interpreted as empty arrays offline. Original proof/runner/JSON remain byte-exact.'))
    controls=[]
    for key,value in [('grant_sequence',[4]),('incremental_grants',[4]),('expected_owned',17)]:
        bad=copy.deepcopy(n);bad['cases'][0]['q'][key]=value
        try:literal_plan(bad,cfg)
        except AssertionError:controls.append(dict(kind='reject-NORMAL-'+key,rejected=True))
        else:raise AssertionError('Nonempty/wrong NORMAL plan admitted')
    bad=copy.deepcopy(n);bad['cases'][1]['q']['grant_sequence']={}
    try:literal_plan(bad,cfg)
    except AssertionError:controls.append(dict(kind='reject-other-case-empty-object',rejected=True))
    else:raise AssertionError('Another case empty object admitted')
    for field,value in [('passed',False),('hits',0),('naturalPoolEmpty',False)]:
        bad=copy.deepcopy(fixed);bad['cases'][0]['stages'][1][field]=value
        try:native_cases(bad,cfg)
        except AssertionError:controls.append(dict(kind='reject-contact-'+field,rejected=True))
        else:raise AssertionError('Missing native outcome admitted')
    put(a.output/'offline-negative-controls.json',controls)
    source=D/'final-bill-lance-hard-gallery-source-v2/emission-controls.json'
    source_rows=json.loads(source.read_text())['rows'];measured=[]
    for q in fixed['cases']:
        for s in q['stages']:
            expected=next(z for z in source_rows if z['variant']==cfg['variant'] and z['case']==q['q']['name'] and z['face']==s['face'])
            actual={abs(z['vx']-65536 if z['vx']>=32768 else z['vx'])for z in s['spawns']}
            assert actual=={expected['horizontal_q8_speed']}
            times=[z['update']for z in s['spawns']]
            if s['kind']=='auto-cadence':assert [y-x for x,y in zip(times[:5],times[1:6])]==[7,7,6,7,6]
            measured.append(dict(case=q['q']['name'],task=s['kind'],face=s['face'],
                                 native_abs_Q8_speeds=sorted(actual),source_abs_Q8_speed=expected['horizontal_q8_speed'],
                                 emission_updates=times))
    put(a.output/'actual-speed-cadence-vs-compiled-source.json',measured)
    # Native runner independently parsed every physical DMA and PPU/cadence row.
    # Reparse literal DMA stream here, including all 256 byte-write ordinals.
    counts=dict(complete256DMAs=0,startFrame_epochs=0,scoped_enables=0,late_scoped_enables=0)
    last=None
    for line in(native/'ability-dma-epochs.jsonl').open():
        q=json.loads(line)
        if q['kind']=='completed-DMA-before-render-enable':
            counts['complete256DMAs']+=1
            assert q['id']==counts['complete256DMAs'] and q['page']==2
            assert len(q['source'])==len(q['hardware'])==len(q['writes'])==256 and q['source']==q['hardware']and not q['differences']
            assert q['start']['mask']&24==q['complete']['mask']&24==0 and q['start']['oamaddr']==q['complete']['oamaddr']==0
            assert q['start']['pc']==cfg['dma_protocol']['window_start'] and q['complete']['pc']==cfg['dma_protocol']['complete_pc']
            for i,w in enumerate(q['writes']):assert w['stamp']['oamaddr']==i and w['stamp']['mask']&24==0 and w['value']==q['source'][i]
            last=q
        elif q['kind']=='startFrame-hardware':
            counts['startFrame_epochs']+=1;assert len(q['hardware'])==256
            if q.get('completed_dma_id') and not q.get('pending_dma_id'):assert last and q['completed_dma_id']==last['id'] and q['hardware']==last['source']
        elif q['kind']=='actual-PPUMASK-write' and q['scoped'] and q['enabling']:
            counts['scoped_enables']+=1;s=q['stamp']
            assert q['safe'] and(241<=s['scanline']<=260 or s['scanline']==-1 and s['cycle']<=274)
    assert counts['complete256DMAs']>100 and counts['scoped_enables']>100
    for k in ['actual_full_PPU','hardware','cadence']:assert original['analysis']['components'][k]['passed']
    captures={}
    for line in(native/'events.jsonl').open():
        q=json.loads(line)
        if q['kind']=='ppu-frame-captured':captures[q['data']['name']]=q
    selected=[]
    for q in cfg['cases']:
        for suffix in ['committed-HUD','1-source-art','real-contact','3-source-art','4-source-art']:
            name=q['name']+'-'+suffix;f=native/(name+'.argb');ev=captures[name];raw=f.read_bytes()
            with(native/'actual-ppu.argb').open('rb')as data:
                data.seek((ev['wall']-1)*245760);assert data.read(245760)==raw
            selected.append(dict(name=name,raw=str(f),sha256=sha(f),PPU_ordinal=ev['wall'],
                                 native_capture_event=ev,source='Exact 256x240 complete raw frame; byte-equal to that full-PPU ordinal.'))
    for page,start in enumerate([0,20],1):
        page_rows=selected[start:start+20];rows=(len(page_rows)+4)//5
        im=Image.new('RGB',(5*268+12,rows*270+12),(31,43,57));draw=ImageDraw.Draw(im)
        for i,z in enumerate(page_rows):
            x=12+(i%5)*268;y=12+(i//5)*270
            draw.rectangle((x-2,y+22-2,x+257,y+22+241),outline=(239,190,56),width=2)
            draw.text((x,y),z['name'],fill='white');draw.text((x,y+10),'PPU '+str(z['PPU_ordinal']),fill=(183,205,222))
            frame=Image.frombytes('RGBA',(256,240),Path(z['raw']).read_bytes(),'raw','BGRA').convert('RGB')
            im.paste(frame,(x,y+22))
        im.save(a.output/('whole-frame-review-'+str(page)+'.png'))
    put(a.output/'review-files.json',dict(placements=selected,sheets=[str(a.output/('whole-frame-review-'+str(i)+'.png'))for i in [1,2]],
        visual_review='PENDING agent review; no all-frame graphical cleanliness claim.'))
    put(a.output/'proof.json',dict(freeze_complete=True,offline_schema_local_comparison_passed=True,
        original_host_aggregate_passed=original['passed'],original_host_proof_sha256=sha(native/'proof.json'),
        original_host_error=original['analysis']['errors'],native_run=False,new_native_launches=0,
        original_native_launches=1,worker_released=True,ROM_sha256=SHA,profile=a.profile,
        ready_bindings_verified=verified,exact_two_empty_array_paths=diffs,negative_controls=len(controls),
        native_cases=cases,native_speeds_and_cadence_compared=len(measured),hardware=counts,
        PPU=original['analysis']['components']['actual_full_PPU'],cadence=original['analysis']['components']['cadence'],
        native_source_requests='Actual original native assertion certified source fire/pickup requests; no waveform claim.',
        Lance='UNRUN: conditional original-host PASS was not met; no launch authorised by this offline comparison.',
        limits='B controlled already-mature-item physical collision/grant/use. No block reveal/rise/random drop campaign, native waveform or all-frame visual qualification. Original aggregate FALSE remains immutable.'))
    files={Path(__file__),ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py',a.ready/'proof.json',a.ready/'manifest.json',source}
    files.update(f for f in native.iterdir()if f.is_file());files.update(a.output.iterdir())
    bindings={Path(z['path']):z['sha256']for z in json.loads((a.ready/'manifest.json').read_text())['bindings']}
    for f,h in bindings.items():assert sha(f)==h,f
    bindings.update({f:sha(f)for f in files})
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
    print(json.dumps(dict(original_aggregate_FALSE=not original['passed'],offline_comparison_passed=True,
        proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),
        worker_released=True,Lance_unrun=True)))


if __name__=='__main__':main()
