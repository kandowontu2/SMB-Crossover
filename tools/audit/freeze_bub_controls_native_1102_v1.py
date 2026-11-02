"""Retain CF/BT and Bub controls evidence before root-only capture cleanup."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
O=R/'build/bub-menu-candidate-1102-v2'
D=R/'docs/qa/checkpoints/2026-11-02/bub-controls-native-v1'
PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'

def main():
    assert sha(O/'combined-visible.nes')==PIN and not D.exists()
    files=[];safe=[];runs=[]
    for folder,passed,frames in [('native-visible-cf-start',True,860),
        ('native-source-bub-controls',False,1257),('native-source-bub-controls2',True,1257),
        ('native-visible-bt-start2',True,740)]:
        packet=O/folder;capture=packet/'capture'
        ready=json.loads((packet/'ready.json').read_text());binding=json.loads((capture/'binding.json').read_text())
        assert ready['ROM_sha256']==binding['ROM_sha256']==PIN
        assert binding['exit_code']==(0 if passed else 1)
        for path,digest in ready['bindings'].items():assert sha(path)==digest,path
        result=json.loads((capture/'result.json').read_text())if(capture/'result.json').exists()else None
        observer=json.loads((capture/'bub-observer.json').read_text())if(capture/'bub-observer.json').exists()else None
        if passed:assert result['passed'] and result['frames']==frames
        else:
            assert result is None and observer['failures']==49 and observer['physical_frames']==frames
            assert 'Passive original source/header/hardware assertions'in(capture/'combined-visible-controller.log').read_text(errors='replace')
        if folder.endswith('controls2'):
            assert observer['passed'] and observer['checks']==3080 and observer['failures']==0
            assert observer['source_cache_last_draw_differences']==49 and observer['launches']==1
        generated=[p for p in packet.rglob('*')if p.is_file()]
        assert sum(p.suffix.lower()=='.png'for p in generated)<=4
        files+=generated;safe +=[p.relative_to(R).as_posix()for p in capture.iterdir()if p.is_file()]
        runs.append(dict(packet=folder,passed=passed,frames=frames,result=result,observer=observer,
            scope='Initial v2 observer compares newer source cache against lastdraw; v3 actual pair inputs/both halves qualify hardware without ROM changes.'if not passed else
                  'Actual original idle/walk/reverse/43pxjump/landing/freshBbubble; no trap/pop/release or full-stage proof.'if 'controls'in folder else
                  'Existing CF Select/confirm gameplay handoff.'if'cf-start'in folder else
                  'ExactStart32 followed by legitimate body-color lease96; private BtVariant32/ready1; original negative retained.'))
    files +=[O/n for n in['combined-visible.json','combined-visible.dbg','combined-visible.lbl','BT-Start-palette-CPU-v2.json']]
    files +=[R/'tools/audit'/n for n in[Path(__file__).name,'bub_native_controls_1102_v1.lua',
        'prepare_bub_native_controls_1102_v1.py','prepare_bub_native_controls_1102_v2.py',
        'check_bub_bt_start_1102_v2.py','prepare_bub_bt_regression_1102_v2.py','bub_menu_qualification_1102_v2.lua']]
    files +=[R/'build/bubble-bobble-source-1101-v1'/n for n in[
        'native-observer-bub-1102-v2.lua','native-observer-bub-1102-v3.lua',
        'native-observer-prepared-1102-v2.json','native-observer-prepared-1102-v3.json']]
    files +=[R/'docs/qa/allocations/bubble-visible-1102-v6.json'];files=list(dict.fromkeys(files))
    hashes={p.relative_to(R).as_posix():sha(p)for p in files};D.mkdir(parents=True)
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None and set(z.namelist())==set(hashes)
        for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    q=dict(passed=True,partial_native_qualification=True,private_native_only=True,ROM_SHA256=PIN,
        installed=False,production_admitted=False,full_stage=False,helpers_added=False,
        source_controls_Bub_passed=True,source_controls_Bob_qualified=False,earned_combat_qualified=False,
        Easy_stomp_qualified=False,actual_native=runs,
        prior_BT_exact_groups_negative_corrected_by_actual_CPU_and_native=True,
        archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archived_files=hashes,
        remaining=['Actual earned source trap/timeout/pop/native defeat','Bob movement/combat','Easy policy','Terrain/full1-1 and eventual Downloads delivery'],
        exact_capture_files_safe_for_root_to_remove_after_bytecompare=safe,
        keep_live_controllers_readies_runs=True,
        scope='Four exact actual run receipts, unique sources and original observer negative retained compactly; no emulator, ROM change or install.')
    (D/'manifest.json').write_text(json.dumps(q,indent=2)+'\n')
    staging=['tools/audit/'+n for n in['bub_native_controls_1102_v1.lua','prepare_bub_native_controls_1102_v1.py',
        'prepare_bub_native_controls_1102_v2.py','check_bub_bt_start_1102_v2.py','prepare_bub_bt_regression_1102_v2.py',Path(__file__).name]]
    staging +=[(D/n).relative_to(R).as_posix()for n in['inputs.zip','manifest.json','commit-files.txt']]
    (D/'commit-files.txt').write_text('\n'.join(staging)+'\n')
    print(json.dumps(dict(checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        safe_capture_files=len(safe),safe_capture_bytes=sum((R/p).stat().st_size for p in safe),ROM_changed=False,installed=False)))

if __name__=='__main__':main()
