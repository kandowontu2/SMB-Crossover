"""Archive this complete native batch, including all source and observer negatives."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
O=R/'build/bub-menu-candidate-1102-v2';B=R/'build/bubble-bobble-source-1101-v1'
D=R/'docs/qa/checkpoints/2026-11-02/bub-controls-combat-native-v2'
PIN='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'

def main():
    assert sha(O/'combined-cold-fixed.nes')==PIN and not D.exists()
    entries=[('native-earned-bub-timeout',0),('native-earned-bub-pop',1),('native-earned-bub-pop2',1),
        ('native-earned-bub-pop3',1),('native-stomp-bub-easy',1),('native-stomp-bub-controls',1),
        ('native-cold-fixed-bub',0),('native-cold-fixed-bob',0),('native-cold-fixed-bub-controls',0),
        ('native-cold-fixed-bob-controls',0),('native-cold-fixed-bub-easy',1),('native-cold-fixed-bub-pop',1),
        ('native-cold-fixed-bub-pop2',0)]
    files=[];safe=[];runs=[]
    for folder,code in entries:
        packet=O/folder;capture=packet/'capture';ready=json.loads((packet/'ready.json').read_text());binding=json.loads((capture/'binding.json').read_text())
        assert binding['exit_code']==code and binding['ROM_sha256']==ready['ROM_sha256']
        for name,digest in ready['bindings'].items():assert sha(name)==digest,name
        result=json.loads((capture/'result.json').read_text())if(capture/'result.json').exists()else None
        observer=json.loads((capture/'bub-observer.json').read_text())if(capture/'bub-observer.json').exists()else None
        custom={}
        for name in['source-controls.json','easy-stomp.json','earned-combat.json']:
            if(capture/name).exists():custom[name]=json.loads((capture/name).read_text())
        if code==0:assert result and result['passed']
        else:assert result is None
        if folder=='native-cold-fixed-bub-pop2':
            q=custom['earned-combat.json'];assert q['passed'] and q['actual_native_defeat_entries']==1
            assert q['source']['captures']==q['source']['pops']==1 and q['source']['failures']==0
            assert q['initial_lives']==q['final_lives']==2
        generated=[p for p in packet.rglob('*')if p.is_file()]
        assert sum(p.suffix.lower()=='.png'for p in generated)<=4
        files+=generated;safe +=[p.relative_to(R).as_posix()for p in capture.iterdir()if p.is_file()]
        runs.append(dict(packet=folder,passed=code==0,ROM_SHA256=ready['ROM_sha256'],result=result,observer=observer,custom=custom))
    sources=['compose_bub_stomp_1102_v7.py','compose_bub_cold_fixed_1102_v8.py','bub_native_combat_1102_v1.lua',
        'prepare_bub_native_combat_1102_v1.py','prepare_bub_native_pop_1102_v2.py','prepare_bub_native_pop_1102_v3.py',
        'prepare_bub_stomp_controls_1102_v7.py','bub_native_easy_1102_v7.lua','prepare_bub_native_easy_1102_v7.py',
        'prepare_bub_cold_fixed_native_1102_v8.py','prepare_bub_current_packets_1102_v8.py','prepare_bub_current_pop_1102_v9.py',
        'prepare_bub_current_pop_observer_1102_v10.py','audit_andre_attack_geometry_1102_v1.py',Path(__file__).name]
    files +=[R/'tools/audit'/n for n in sources]
    files +=[O/n for n in['combined-stomp.json','combined-cold-fixed.json','combined-cold-fixed.dbg','combined-cold-fixed.lbl','andre-attack-geometry-CPU-v1.json']]
    files +=[R/'docs/qa/allocations'/n for n in['bubble-stomp-1102-v7.json','bubble-cold-fixed-1102-v8.json']]
    files +=[B/n for n in['native-stomp-successor-4395.json','native-stomp-qualified-1102-v7.json',
        'native-cold-fix-successor-31c0.json','native-cold-fix-qualified-1102-v8.json','original-pop-push-CPU.json',
        'native-observer-bub-1102-v3.lua','native-observer-bub-1102-v4.lua','native-observer-bub-1102-v5.lua','native-observer-bob-1102-v5.lua',
        'native-observer-prepared-1102-v3.json','native-observer-prepared-1102-v4.json','native-observer-prepared-1102-v5.json']]
    files=list(dict.fromkeys(files));hashes={p.relative_to(R).as_posix():sha(p)for p in files};D.mkdir(parents=True)
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None and set(z.namelist())==set(hashes)
        for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    q=dict(passed=False,partial_native_qualification=True,private_native_only=True,current_ROM_SHA256=PIN,
        installed=False,production_admitted=False,full_stage=False,helpers_added_by_Bub=False,
        both_current_cold_and_source_controls_passed=True,current_earned_source_pop_native_defeat_passed=True,
        timeout_scope='Original39epoch timeout/positiveflag restoration passed on4395; sourcephase unchanged, current5a8a earnedpop passed.',
        native_Easy_qualified=False,current_negative='Actual Easy route has21originaljumpstarts/noEnemyStomped/no nativebounce; backend traces real ceiling/native-speed feedback and prepares source v9. Do not install5a8a.',
        preserved_negatives=['Three4395pop input attempts timeout as sourcecirclepushes atdx10..12','31c0 admission/importstub omitted; coldhandoffnegative inEasy andcontrols',
            'Current pop1 observer searched oldeventname; physicalcommit schema corrected withsameinputs inpop2'],
        actual_native=runs,archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archived_files=hashes,
        exact_capture_files_safe_for_root_to_remove_after_bytecompare=safe,keep_live_controllers_readies_runs=True,
        remaining=['Source v9 ceiling repair and actual Easy native stomp/bounce','Original freebubble ride and terrain/full1-1','Native source combat/Bob extensions and eventual tested Downloads delivery'],
        scope='Exact source/native batch retained byte-for-byte before root-only cleanup. Prior checkpoints immutable; no new emulator or install.')
    (D/'manifest.json').write_text(json.dumps(q,indent=2)+'\n')
    staging=['tools/audit/'+n for n in sources]+['docs/qa/allocations/bubble-stomp-1102-v7.json','docs/qa/allocations/bubble-cold-fixed-1102-v8.json']
    staging +=[(D/n).relative_to(R).as_posix()for n in['inputs.zip','manifest.json','commit-files.txt']]
    (D/'commit-files.txt').write_text('\n'.join(staging)+'\n')
    print(json.dumps(dict(checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        safe_capture_files=len(safe),safe_capture_bytes=sum((R/p).stat().st_size for p in safe),installed=False)))

if __name__=='__main__':main()
