"""Preserve source plus narrowly qualified facing smokes for the installed WIP."""
from pathlib import Path
import csv
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
P=R/'build/functional-roster-ready54-v1'
O=R/'docs/qa/checkpoints/2026-10-30/functional-roster-ready54'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    assert not O.exists()
    h=json.loads((P/'handoff.json').read_text())
    assert sha(P/'handoff.json')=='8c5ecf42e67f53a046a64de8e93a893956d713e427d84149b6f472d409621876'
    assert all(sha(f)==v for f,v in h['bindings'].items())
    install=R/'docs/qa/functional-roster-ready54-2026-10-30.json'
    installed=json.loads(install.read_text());assert sha(installed['latest'])==h['candidate']
    files=set(map(Path,h['bindings']))|{P/'handoff.json',install,Path(__file__)}
    native=[]
    for name in ['chip','dale']:
        p=R/f'build/current-{name}-facing-smoke-ready54-1030-v1'
        packet=json.loads((p/'native-facing-smoke-packet.json').read_text())
        assert all(sha(f)==v for f,v in packet['bindings'].items())
        r=json.loads((p/'result.json').read_text());review=json.loads((p/'review.json').read_text())
        budget=json.loads((p/'capture-budget.json').read_text())
        assert r['passed'] and review['passed'] and r['zero_deaths'] and r['cheats_off']
        assert not budget['violations'] and r['full_frames']==5
        assert {'menu','facing-right','facing-left','endpoint'}<=set(r['markers'])
        rows=list(csv.DictReader((p/'trace.csv').open(newline='')))
        first=next(row for row in rows if int(row['frame'])==r['markers']['first-active']['frame'])
        actual=int(rows[-1]['loops'])-int(first['loops']);assert actual==75
        visual=dict(reviewed_by='root',status='MENU_AND_SUSTAINED_FACING_VISUAL_PASS',
            montage_sha256=sha(p/'selected-whole-frames.png'),selected_screens=5,
            observations=['Native colored menu preview faces right.',
                          'Sustained right and left movement show the corresponding complete body facing.'],
            actual_completed_updates_after_entrance=75,
            scope_correction='Fixture loops includesstartup; its220-active-update wording is NOT qualified. Actual trace proves75 post-entrance updates, both sustained directions and coldmenu.',
            full_1_1_clear=False,every_frame_visual_review=False)
        save(p/'root-visual-review.json',visual)
        native.append(dict(identity=name,frames=r['frames'],actual_updates=actual,selected_visual=visual,
            source_DMA_bytes=r['unmasked_source_writes_checked'],physical_E3_bytes=r['physical_E3_bytes_checked'],
            CHR_window_checks=r['chr_window_checks'],NMI_checks=r['nmi_checks'],IRQ_checks=r['irq_checks']))
        files.update(map(Path,packet['bindings']))
        files.update(f for f in p.iterdir() if f.is_file())
    # The separate longer route failure is evidence to retain, not a clear.
    negative=R/'build/current-chip-facing-easy-ready54-1030-v2'
    result=json.loads((negative/'result.json').read_text())
    assert not result['passed'] and result['frames']==1956
    files.update(f for f in negative.iterdir() if f.is_file())
    for rel in ['tools/audit/prepare_current_chip_facing_fix_1030_v1.py',
                'build/current-chip-facing-fix-1030-v1/source-proof.json',
                'build/current-chip-facing-fix-1030-v1/source.patch',
                'build/current-chip-facing-fix-1030-v1/selector-controls.json']:
        files.add(R/rel)
    allow={'.s','.inc','.cfg','.py','.lua','.json','.jsonl','.csv','.patch','.md','.txt','.log','.png','.nesppuv1','.dep'}
    files={f for f in files if f.suffix in allow and f.is_relative_to(R)}
    O.mkdir(parents=True);zpath=O/'source-and-native-evidence.zip'
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for f in sorted(files):
            assert not f.read_bytes().startswith(b'NES\x1a'),f
            z.write(f,f.relative_to(R).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==sha(R/n) for n in z.namelist())
    receipt=dict(status='INSTALLED_FUNCTIONAL_WIP_54',ROM_sha256=h['candidate'],
        verified_source_bindings=len(h['bindings']),source_handoff_sha256=sha(P/'handoff.json'),
        ready=54,pending=26,source_checks=h['checks'],native_facing=native,
        retained_full_route_failure=dict(identity='chip',frame=1956,x=2012,reason=result['reason'],clear=False),
        all_character_1_1_and_powerups_complete=False,other_four_requested_facing_fixes_still_pending=True,
        archive_sha256=sha(zpath),archive_bytes=zpath.stat().st_size,archive_members=len(files),
        all_archive_members_verified=True,no_ROM_object_debug_files=True)
    save(O/'receipt.json',receipt)
    print(json.dumps(dict(checkpoint=str(O),bytes=zpath.stat().st_size,members=len(files))))


if __name__=='__main__':main()
