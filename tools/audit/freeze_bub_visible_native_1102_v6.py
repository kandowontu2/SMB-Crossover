"""Persist one compact v6 native checkpoint before root prunes capture copies."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
O=R/'build/bub-menu-candidate-1102-v2'
D=R/'docs/qa/checkpoints/2026-11-02/bub-combined-native-v6'
PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'

def main():
    assert sha(O/'combined-visible.nes')==PIN
    assert not D.exists(),'Native checkpoint is immutable'
    rows=[];files=[];disposable=[]
    for folder,passed,frames in[('native-visible-bub-cold',True,700),('native-visible-bob-cold',True,660),
        ('native-visible-ex-regression',True,1825),('native-visible-sh-regression',True,606),('native-visible-bt-start',False,None)]:
        packet=O/folder;capture=packet/'capture';ready=json.loads((packet/'ready.json').read_text());binding=json.loads((capture/'binding.json').read_text())
        assert ready['ROM_sha256']==binding['ROM_sha256']==PIN
        for path,digest in ready['bindings'].items():assert sha(Path(path))==digest,path
        assert binding['exit_code']==(0 if passed else 1)
        result=json.loads((capture/'result.json').read_text())if(capture/'result.json').exists()else None
        if passed:assert result['passed'] and result['frames']==frames
        else:
            assert result is None
            assert 'Simultaneous Select/confirm preserved identity'in(capture/'combined-visible-controller.log').read_text(errors='replace')
        generated=[p for p in packet.rglob('*')if p.is_file()]
        assert sum(p.suffix.lower()=='.png'for p in generated)<=4
        files +=generated;disposable +=[p.relative_to(R).as_posix()for p in capture.iterdir()if p.is_file()]
        rows.append(dict(packet=folder,passed=passed,frames=frames,result=result,
            scope=('Cold identity/ready/active8 plus nativebackdrop/HUDattributes/name/WORLD/TIME/sourceRGB'if'cold'in folder else'Unchanged delivered Ex or Sh necessary shared-seam regression'if passed else'BT final gameplay variant/persistent FmGroups assertion; cause under investigation, not an admitted ROM regression')))
    files +=[O/n for n in['combined-visible.json','visible-cold-native-v6.json','combined-visible.dbg','combined-visible.lbl','ordered-input-v3/native-menu-plans.json']]
    files +=[R/'tools/audit'/n for n in['compose_bub_visible_1102_v6.py','prepare_bub_visible_regressions_1102_v6.py',Path(__file__).name,'bub_menu_qualification_1102_v2.lua','prepare_bub_menu_qualification_1102_v2.py']]
    files +=[R/'docs/qa/allocations'/n for n in['bubble-shared-native-1102-v5.json','bubble-visible-1102-v6.json']]
    files +=[R/'build/bubble-bobble-source-1101-v1'/n for n in['native-proxy-shared-proposal-1966.json','native-visible-successor-00971.json','native-visible-qualified-1102-v6.json']]
    files +=[R/'build/bub-menu-integration-1102-v1/controls-proposal.json'];files=list(dict.fromkeys(files))
    hashes={p.relative_to(R).as_posix():sha(p)for p in files};D.mkdir(parents=True)
    archive=D/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None and set(z.namelist())==set(hashes)
        for name,digest in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
    q=dict(passed=False,partial_native_qualification=True,ROM_SHA256=PIN,private_native_only=True,installed=False,production_admitted=False,
        source_controls_combat_Easy_full11_qualified=False,helpers_added=False,
        actual_native=rows,root_visual_v6_cold_review_passed=True,
        archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,archived_files=hashes,
        remaining=['Resolve actual BT final FmGroups/identity lifetime without weakening source policy','Run still-unexecuted CF packet','Actual Bub/Bob source controls, bubble contact/pop/release, Easy, terrain/full1-1 and eventual Downloads delivery'],
        exact_capture_files_safe_for_root_to_remove_after_bytecompare=disposable,
        keep_live_controllers_readies_runs=True,
        scope='Compact source/native checkpoint. All actual captures retained byte-for-byte in inputs.zip before root-only scoped cleanup; no new emulator or install.')
    (D/'manifest.json').write_text(json.dumps(q,indent=2)+'\n')
    staging=['tools/audit/compose_bub_visible_1102_v6.py','tools/audit/prepare_bub_visible_regressions_1102_v6.py','tools/audit/'+Path(__file__).name]
    staging +=[(D/n).relative_to(R).as_posix()for n in['inputs.zip','manifest.json','commit-files.txt']]
    (D/'commit-files.txt').write_text('\n'.join(staging)+'\n')
    print(json.dumps(dict(checkpoint=D.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        safe_capture_files=len(disposable),safe_capture_bytes=sum((R/p).stat().st_size for p in disposable),
        controller_or_ready_removed=False,ROM_or_emulator_changed=False)))

if __name__=='__main__':main()
