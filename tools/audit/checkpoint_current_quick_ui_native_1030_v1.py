"""Save the source-routed Quick HUD fix and its bounded native acceptance."""
from pathlib import Path
import csv
import json
from checkpoint_celeste_quick_native_1030_v1 import R, Q, ALLOW, sha, save, verify, archive
from current_roster_compact_11_v1 import linked


def main():
    p = R/'build/current-character-quick-ui-v13'
    s = verify(p/'handoff.json', 'c229c572e469cd3c280cdc03d485ae85c7c70ff10293c72f37c1cec84e2824a3')
    f = p/'native-prepared'
    n = verify(f/'prepared.json', 'ff8c6e8384300877d31079c2cb2b5395e3d65718c8500c04c6831982146bbd0c')
    d = p/'native/cold-menu-ui-v13'
    result = json.loads((d/'result.json').read_text())
    intervals = json.loads((d/'root-ui-span-review.json').read_text())
    assert result['passed'] and result['native'] and not result['debug_RAM_writes']
    assert intervals['passed'] and intervals['genuine_GameLoop_intervals'] == intervals['genuine_QhUi_spans'] == 122
    assert intervals['spans_sha256'] == sha(d/'gameplay-spans.csv')
    old, _, _, _, _ = linked(R/'build/current-character-quick-cold-v12/joint/candidate.nes')
    new, _, address, location, _ = linked(p/'joint/candidate.nes')
    assert sha(p/'joint/candidate.nes') == '7a9e2cc1246d590bebe2acd5451267894f39cdac75cd528e20109de01753d760'
    changes = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
    assert len(old) == len(new) and len(changes) == 28
    start = 16 + 86*8192
    assert all(start+0x5d8 <= i < start+0x5dc or start+0x79c <= i < start+0x7b4 for i in changes)
    assert address('X5OwnInventoryUi') == 0xa5ca and address('X5NewRosterUiRoute') == 0xa786
    profile = json.loads((d/'profile-summary.json').read_text())['aggregate']
    assert profile['QhUi']['calls'] == 122 and profile['QhUi']['min'] == profile['QhUi']['max'] == 65
    game = [r for r in csv.DictReader((d/'frames.csv').open(newline='')) if r['phase'] == 'game']
    assert all(r['HP'] == '40' for r in game)
    visual = dict(reviewed_by='root', images={f.name:sha(f) for f in d.glob('*.png')},
        scope='All four selected complete native PNGs; not every game frame.',
        findings=['HP40 is visible; inherited BUSTER is absent in all selected gameplay frames.',
                  'Quick Man body, fan shots, world blocks and blue backdrop appear coherent.',
                  'Menu name/footer spacing is still crowded; no PPU overwrite is established.'],
        every_frame_visual_review=False, UI_fix_confirmed=True, performance_hold=True)
    save(d/'root-visual-review.json', visual)
    files = {p/'handoff.json', f/'prepared.json', Path(__file__).resolve()}
    for h in [s, n]:
        files.update(Path(name) for name in h['bindings'] if Path(name).suffix in ALLOW)
    for directory in [f, d]:
        files.update(q for q in directory.rglob('*') if q.is_file() and q.suffix in ALLOW)
    archive(Q/'quick-current-source-ui-native-performance-hold', files,
        dict(status='PRIVATE_QUICK_UI_FIX_SOURCE_AND_NATIVE_PASS_PERFORMANCE_HOLD',
             ROM_sha256=n['candidate'], source_handoff_sha256=sha(p/'handoff.json'),
             prepared_sha256=sha(f/'prepared.json'), verified_source_bindings=len(s['bindings']),
             verified_native_bindings=len(n['bindings']), changed_ROM_bytes=28, physical_bank=86,
             genuine_QhUi_per_complete_sampled_Main=1, sampled_Main_calls=122,
             independently_checked_cycle_containment=True, native_smoke_game_frames=220,
             HP=40, BUSTER_absence_hardware_assertions=True, selected_visual_review=visual,
             measured_Main_CPU=dict(calls=122, mean=profile['GameLoop']['inclusive']/122,
                                    max=profile['GameLoop']['max']),
             gameplay_NmiSkipped=[int(game[0]['NmiSkipped']),int(game[-1]['NmiSkipped'])],
             observer_correction='The strengthened observer was bound but unused. Original v6 profile actually ran; mandatory root interval/count acceptance passes separately.',
             no_paired_native_speedup_or_cadence_claim=True, admitted=False, installed=False))


if __name__ == '__main__':
    main()
