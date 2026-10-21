"""Pin actual current-ROM clears and retain private negatives without promotion."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/verification/root-current49-progress-s.json'


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def pin(p):
    p = Path(p)
    return dict(path=p.relative_to(R).as_posix(), bytes=p.stat().st_size, sha256=sha(p))


def main():
    assert not OUT.exists(), 'Fresh snapshot only'
    cp = R / 'build/checkpoints/roster-audit-v49-menu-options-s2'
    manifest = json.loads((cp / 'manifest.json').read_text())
    assert manifest['status'] == 'PASS_WORKING_MENU_OPTIONS_BOTH_MAPPERS'
    assert len(manifest['source_hashes']) == 410
    assert all(sha(R / n) == h for n, h in manifest['source_hashes'].items())
    for row in manifest['builds']:
        for item in row['outputs'].values():
            assert sha(R / item['path']) == item['sha256']
            assert sha(cp / Path(item['path']).name) == item['sha256']
    runs = [
        'root49s2-mario-final-a-0-v0-mmc3',
        'root49s2-mario-m5-final-a-0-v0-mmc5',
        'root49s2-luigi-final-a-8-v0-mmc3',
        'root49s2-luigi-m5-final-a-8-v0-mmc5',
    ]
    proofs = []
    flags = ['split_timing_candidates', 'lag_chr_change_candidates', 'motion_candidates',
             'video_vertical_shift_candidates', 'video_background_flash_candidates',
             'audio_events_needing_priority_or_audible_review', 'illegal_guest_native_stomps']
    for name in runs:
        p = R / 'build/roster-through-2-2' / name
        m = json.loads((p / 'manifest.json').read_text())
        v = json.loads((p / 'review.json').read_text())
        assert m['verified_through_2_2'] and m['recording_verified']
        assert m['controller_only'] and not m['memory_or_register_writes']
        assert m['result']['deaths'] == 0 and m['result']['all_six_stages']
        assert v['every_recorded_frame_decoded'] and not v['video_error']
        assert all(not v[f] for f in flags)
        assert m['rom_sha256'] == sha(cp / ('smb-crossover-' + m['config']['mapper'] + '.nes'))
        assert sha(p / 'inputs.csv') == m['inputs_sha256']
        assert sha(p / 'playthrough.mp4') == m['recording_metadata']['mp4_sha256']
        proofs.append(dict(run=name, character=m['config']['character'],
            mapper=m['config']['mapper'], frames=m['result']['frames'],
            files={n: pin(p / n) for n in ['manifest.json', 'review.json', 'inputs.csv',
                                         'playthrough.mp4', 'native.avi', 'review-contact-1.png']},
            scope='Ordinary fixed power-on route through 2-2; small form throughout, not upgrade coverage.',
            lag_hardware_frames=v['lag_hardware_frames'],
            overloaded_sprite_frames=v['overloaded_sprite_frames']))
    bill = R / 'build/verification/root49s2-e-bill-full-m3-a-review.json'
    b = json.loads(bill.read_text())
    assert b['status'] == 'FAIL_UNADMITTED_NATIVE_COVERAGE'
    assert not b['source_projection_mismatches'] and len(b['missing_actual_paths']) == 10
    refs = [
        'build/verification/root-current49-progress-r.json',
        'build/checkpoints/roster-audit-v49-menu-options-s2/manifest.json',
        'build/verification/root49-menu-validation-s2.json',
        'build/verification/agent-lsr-s2-head-n2-a/report-b.json',
        'build/verification/agent-lsr-s2-head-n2-a/actual-review.json',
        'build/verification/root49s2-e-bill-smoke-a-review.json',
        'build/verification/root49s2-e-bill-full-m3-a-review.json',
        'build/verification/agent49-s2-mm-bass-routes/handoff-c.json',
        'build/verification/agent49s2-samus-contra/handoff-d.json',
        'build/verification/specialist-scrooge-s2/mario-luigi-media-review.json',
        'build/verification/root49s2-scrooge-phase-search-b/preparation.json',
        'docs/qa/roster-provisional-v49.md',
        'docs/qa/menu-options-v49.md',
    ]
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 50_000_000_000
    report = dict(status='progress-full-goal-incomplete', goal_complete=False,
        accepted_release=False, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        script=pin(Path(__file__)), main_source410_exact=True,
        root_ROM_DBG_LBL_MAP_LST_exact=True, requested_menu_complete=True,
        character_select_contains_options=False, default_behavior='1.0', default_shadows='OFF',
        retained_current_S2_recorded_fixed_clears=proofs,
        references=[pin(R / n) for n in refs],
        workspace_bytes=used, cap_bytes=50_000_000_000, retain_lossless_captures=True,
        root_live_native_CPU_compile_jobs=[],
        specialist_discovery_active=['link_simon_ryu', 'pit_rygar_sophia', 'mario_luigi_scrooge_s2'],
        private_fixes_not_promoted=['Ryu S2 plus head N2', 'Bill O2 plus body-shape B'],
        bill_actual_46_scope=dict(observed_projection_mismatches=0, missing_actual_paths=10,
                                  passing_full_component=False),
        unfinished=[
            'Remaining ordinary full-roster/alternate routes and retained fixed final recordings through 2-2.',
            'Every special, alternate weapon and upgrade, including genuine ordinary pickup coverage.',
            'Private Ryu fix review and functional mode/contact controls before promotion.',
            'Bill component arena admission repairs and source integration/bank-budget work.',
            'Lag optimization and source geometry/audio fidelity work, including firebar bitmap differences.',
            'Current recordings must be rerun if later runtime changes alter their checkpoint.'])
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(path=str(OUT), sha256=sha(OUT), workspace_bytes=used,
                          recorded_current_clears=len(proofs))))


if __name__ == '__main__':
    main()
