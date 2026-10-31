"""Freeze the RCR misc-sprite repair and both unchanged-controller native routes."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
S=R/'build/current-rcr-misc-chr-fix-1030-v1'
OLD=R/'build/current-alex-easy-11-1030-v1'
NEW=R/'build/current-alex-easy-rcr-fixed-11-1030-v1'
O=R/'docs/qa/checkpoints/2026-10-30/current-rcr-native-misc-repair'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    assert not O.exists()
    source=json.loads((S/'source-proof.json').read_text())
    for f,h in source['bindings'].items():assert sha(f)==h,f
    assert source['changed_ROM_bytes']==409
    before=list(csv.DictReader((OLD/'trace.csv').open(newline='')))
    after=list(csv.DictReader((NEW/'trace.csv').open(newline='')))
    assert len(before)==len(after)==4490
    assert (OLD/'inputs.csv').read_bytes()==(NEW/'inputs.csv').read_bytes()
    differences=[]
    for a,b in zip(before,after):
        changed={k:[a[k],b[k]] for k in a if a[k]!=b[k]}
        if changed:
            assert set(changed)=={'loopCycles','interruptCycles'}
            assert all(int(y)-int(x)==1 for x,y in changed.values())
            differences.append(dict(frame=int(a['frame']),fields=changed))
    assert [d['frame'] for d in differences]==[793,3191]
    files={Path(__file__),R/'tools/audit/prepare_current_rcr_misc_chr_fix_1030_v1.py',
        R/'tools/audit/current_city_route_1030_v1.py'}
    for p in (OLD,NEW):
        h=json.loads((p/'native-city-packet.json').read_text())
        for f,digest in h['bindings'].items():assert sha(f)==digest,f
        result=json.loads((p/'result.json').read_text())
        review=json.loads((p/'review.json').read_text())
        budget=json.loads((p/'capture-budget.json').read_text())
        assert result['passed'] and result['zero_deaths'] and result['cheats_off'] and review['passed']
        assert result['real_1_2_control_updates']>=25 and result['full_frames']==7
        assert not budget['violations'] and budget['final']['bytes']<536870912
        files.update(Path(f) for f in h['bindings'] if Path(f).suffix in {'.py','.lua','.json'})
        files.update(f for f in p.iterdir() if f.is_file())
    visual=dict(reviewed_by='root',status='SELECTED_NATIVE_MISC_VISUAL_PASS',
        montage_sha256=sha(NEW/'selected-whole-frames.png'),selected_screens=7,
        findings=['Mushroom, bumped used block, score popups and moving platform use native artwork.',
                  'RCR body and intrinsic ink remain coherent in selected scenes including underground entry.'],
        every_frame_visual_review=False,complete_campaign_or_audio_claim=False)
    save(NEW/'root-visual-review.json',visual)
    save(S/'native-route-comparison.json',dict(passed=True,inputs_byte_exact=True,
        compared_trace_rows=4490,all_game_controller_position_camera_power_fields_exact=True,
        foreground_cycles_exact=True,trace_byte_exact=False,only_differences=differences))
    files.update({NEW/'root-visual-review.json',S/'native-route-comparison.json'})
    files.update(Path(f) for f in source['bindings'] if Path(f).is_relative_to(S)
                 and Path(f).suffix in {'.s','.inc','.cfg','.json','.patch'})
    files.update({S/'source-proof.json',S/'pixel-and-window-proof.json'})
    files={f for f in files if f.suffix in {'.py','.lua','.s','.inc','.cfg','.json','.patch','.csv','.jsonl','.log','.png','.nesppuv1'}}
    O.mkdir(parents=True)
    zpath=O/'source-and-native-evidence.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for f in sorted(files):
            assert f.is_relative_to(R) and not f.read_bytes().startswith(b'NES\x1a')
            z.write(f,f.relative_to(R).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==sha(R/n) for n in z.namelist())
    receipt=dict(status='SOURCE_AND_NATIVE_MISC_REPAIR_PASS',ROM_sha256=source['ROM_sha256'],
        source_changed_bytes=409,source_pixels_preserved=408,source_records=72,
        source_proof_sha256=sha(S/'source-proof.json'),
        native_frames=4490,completed_loops=3905,controlled_1_2_updates=25,zero_deaths=True,cheats=False,
        controller_and_gameplay_trace_exact=True,only_two_one_cycle_ISR_differences=True,
        selected_visual_review=visual,old_visual_failure_retained=True,
        every_frame_visual_review=False,every_character_campaign_qualified=False,
        archive_bytes=zpath.stat().st_size,archive_sha256=sha(zpath),archive_members=len(files),
        all_archive_members_verified=True,no_ROM_objects_debug=True,installed=False)
    save(O/'receipt.json',receipt)
    print(json.dumps(dict(checkpoint=str(O),members=len(files),bytes=zpath.stat().st_size)))

if __name__=='__main__':main()
