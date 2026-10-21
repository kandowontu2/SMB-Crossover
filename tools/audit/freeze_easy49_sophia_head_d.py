"""Review and freeze the complete scoped head repair before main adoption."""
from pathlib import Path
import csv,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))


def main():
    out=D/'freeze-k.json';assert not out.exists()
    parent=R/'build/checkpoints/roster-audit-v49-combined-ground-audio-samus-c/manifest.json'
    assert sha(parent)=='7bde77980e47d11ed78b9348384016b1a805ff40a02ff180b33f0e8e727b5305'
    c=json.loads(parent.read_text());cat=json.loads((D/'preparation.json').read_text())['source_sha256']
    assert len(cat)==len(c['source_hashes'])==455
    for n,h in cat.items():assert sha(D/'source'/n)==h,n
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    changes=[n for n in cat if cat[n]!=c['source_hashes'][n]]
    assert changes==['src/sophia_source_terrain.s']
    for n,h in c['generated11'].items():assert sha(D/'source/build/generated'/n)==sha(R/'build/generated'/n)==h
    review=V/'agent-lsr-samus-current-c-route-a/sophia-axis-d-source-review.json'
    assert sha(review)=='9c832843e816739bb39bdd2bd2ed84db2cf94ba173c14048eb0af30696303b68'
    assert json.loads(review.read_text())['source_sha256']==cat[changes[0]]
    for n in ['compiled-axis-c.json','compiled-original96-d.json','complete-head-span-c.json','origin-and-query-d.json','origin-stack-k.json','native-head-review-e.json']:
        assert json.loads((D/n).read_text())['status'].startswith('PASS'),n
    profile=json.loads((D/'profile-review.json').read_text())
    assert all(not m['canonical_differences']for m in profile['maps'])
    assert all(s['physicalFrames'][0]==s['physicalFrames'][1]and s['skippedNmis'][0]==s['skippedNmis'][1]and s['physicalDmas'][0]==s['physicalDmas'][1]for m in profile['maps']for s in m['scenes'])
    native=json.loads((D/'native-head-review-e.json').read_text())
    assert sum(len(m['strict_reexecutions'])for m in native['maps'])==109
    assert all(not m['actual_interrupt_gaps']and all(z['cycle_delta']==0 for z in m['strict_reexecutions'])for m in native['maps'])
    helper=V/'agent49k-samus-water-up-direction-component-a/image.py'
    spec=importlib.util.spec_from_file_location('head_freeze_image',helper)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    builds=[];routeproofs=[]
    for mapper in ['mmc3','mmc5']:
        stem=f'smb-crossover-{mapper}'
        im=m.Image(D/f'source/build/{stem}.nes')
        old=m.Image(V/f'root49-combined-working-c/source/build/{stem}.nes')
        assert im.ram==old.ram
        aseg={s['name']:s for s in old.segs.values()}
        for b in im.segs.values():
            a=aseg.get(b['name'])
            if a:
                assert a['start']==b['start']and a.get('ooffs')==b.get('ooffs'),b['name']
                if b['name']!='SOPHIA_TERRAIN_COLD':assert a['size']==b['size'],b['name']
        seg=aseg['SOPHIA_TERRAIN_COLD'];query=old.hook('SophiaTerrainQuery')['address']
        op=bytes([0x20,query&255,query>>8])
        calls=[i for i in range(seg['ooffs'],seg['ooffs']+seg['size']-2)if old.raw[i:i+3]==op]
        assert len(calls)==3
        head=old.hook('Separate','SophiaSourceHeadProbe')['rom_offset']
        append=im.hook('SophiaHeadSourceAxis')['rom_offset']
        size=im.sym('SophiaHeadSourceAxis')['size']+im.sym('SophiaTerrainBoundedQuery')['size']
        assert append==seg['ooffs']+seg['size']and old.raw[append:append+size]==b'\xff'*size
        allowed=set(range(head,head+5))|set(range(append,append+size))
        for p in calls:allowed.update(range(p,p+3))
        delta=[i for i,(a,b)in enumerate(zip(old.raw,im.raw))if a!=b]
        assert all(i in allowed for i in delta)
        assert old.raw[:16]==im.raw[:16]and old.raw[16+512*1024:]==im.raw[16+512*1024:]
        baseline=D/f'source/build/{stem}-baseline.nes'
        assert baseline.read_bytes()==(V/f'root49-combined-working-c/source/build/{stem}-baseline.nes').read_bytes()
        builds.append(dict(mapper=mapper,metadata=im.metadata(),ROM_changed_bytes=len(delta),appended_bytes=size,
                           baseline_sha256=sha(baseline),old_RAM_segments_header_CHR_audio_literal_except_exact_whitelist=True))
        p=R/f'build/roster-through-2-2/root49-sophia-stage1-fixed-j-11-v0-{mapper}'
        discovery=R/f'build/roster-through-2-2/root49-sophia-origin-discovery-i-11-v0-{mapper}'
        z=json.loads((p/'manifest.json').read_text());a=json.loads((p/'result.json').read_text())
        assert z['full_frame_audit']and z['controller_only']and not z['memory_or_register_writes']
        assert z['rom_sha256']==sha(im.path)and not z['verified_through_2_2']
        assert a['failure']=='frame limit'and not a['deaths']and not a['cleared']
        assert a['stage_entries']['0-1']==(4335 if mapper=='mmc3' else 4251)
        t=rows(p/'trace.csv');before=rows(discovery/'trace.csv')
        assert t==before[:len(t)]
        inputs=rows(p/'inputs.csv');assert inputs==rows(discovery/'inputs.csv')[:len(inputs)]
        identity=json.loads((p/'current-c-identity.json').read_text());assert identity['character']==11 and identity['behavior']==0 and identity['outlinesOff']==1
        routeproofs.append(dict(mapper=mapper,frames=len(t),entered_1_2=a['stage_entries']['0-1'],
                                all_trace_fields_exact_to_ordinary_discovery=True,controller_only=True,zero_deaths=True,
                                full_2_2_clear=False,files={q.name:dict(bytes=q.stat().st_size,sha256=sha(q))for q in p.iterdir()if q.is_file()}))
    sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
    size=workspace_bytes(R);assert size+50000000<70000000000
    receipt={str(p.relative_to(D)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in D.rglob('*')if p.is_file()and '__pycache__'not in p.parts}
    result=dict(status='FROZEN_REVIEWED_PROVISIONAL_SOPHIA_NORMAL_FLAT_HEAD_AXIS_D',script_sha256=sha(__file__),
                parent_checkpoint_sha256=sha(parent),source_sha256=cat,source_changes=changes,generated11=c['generated11'],
                builds=builds,stage1_routeproofs=routeproofs,independent_source_review=dict(path=str(review.relative_to(R)),sha256=sha(review)),
                mathematical_cases=27926,actual_full_head_reexecutions=109,foreign_full_caller_component_cases=26,
                native_in_call_interrupts_observed=0,profile=profile,receipt_catalog=receipt,workspace_bytes=size,
                limits=['Scope is normal-flat head-corner routing and origin query clipping. Flash deferred Ground-list scheduling and rotated anchors remain separate.',
                        'No IRQ/NMI occurred inside captured head calls; this packet does not claim new interrupted-corner coverage.',
                        'Seeded origin cases include explicit whole-stack/RAM/write oracle, not natural origin-controller acquisition proof.',
                        'Both independent fixed routes clear1-1 only; later1-2 controller deaths are retained and full2-2 remains required.',
                        'The12cycle query guard costs84/92foreground cycles per stand/walk update in four measured scenes; physical spans, skips, DMA and204canonical fields remain exact.',
                        'No final recording, all-arsenal, source-perfect or all-roster completion claim. Existing73 legacy native failures remain open.'],
                main_changed=False,provisional_admission=True,accepted_release=False,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],sha256=sha(out),ROMs={b['mapper']:b['metadata']['rom']['sha256']for b in builds},workspace_bytes=size)))


if __name__=='__main__':main()
